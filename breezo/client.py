import os
import requests
from six.moves.urllib.parse import quote
import pandas as pd


class ConfigClient:
    star = '*'

    def __init__(self):
        self.version = "Breeze 1.0"
        self.properties = None

    def display(self):
        return self.version

    @staticmethod
    def fetch_env_tuple():
        breezo_url = os.getenv('BREEZO_API_URL', None)
        breezo_env = os.getenv('BREEZO_ENV', None)

        if breezo_url is None:
            raise ValueError('BREEZO_API_URL is not set')

        if breezo_env is None:
            raise ValueError('BREEZO_ENV is not set')

        return breezo_url, breezo_env

    @staticmethod
    def __get_service_url(service_name):
        breezo_url, breezo_env = ConfigClient.fetch_env_tuple()
        return 'http://{}/services/_name/{}?tenant={}'.format(breezo_url, quote(service_name), breezo_env)

    @staticmethod
    def __get_properties_url(service_id):
        breezo_url, breezo_env = ConfigClient.fetch_env_tuple()
        return 'http://{}/services/{}/properties?tenant={}'.format(breezo_url, service_id, breezo_env)

    @staticmethod
    def __fetch_service_id(service_name):
        url = ConfigClient.__get_service_url(service_name)
        response = requests.request("GET", url)

        if response.ok:
            service_resp = response.json()
            if 'data' in service_resp and 'service_id' in service_resp['data']:
                return service_resp['data']['service_id']
            else:
                raise ValueError('failed to fetch service id by service name {}. Please ensure service name is added.'.format(service_name))
        else:
            response.raise_for_status()

    def __evaluate_value(self, field_name, tenant_name, ip):

        properties_copy_df = self.properties.copy(deep=True)

        # step 1: check by ip
        matching_properties_df = properties_copy_df[(properties_copy_df.ip == ip)
                                                     & (properties_copy_df.field_name == field_name)]

        # step 2: if no results then check for all ip
        if matching_properties_df.empty:
            matching_properties_df = properties_copy_df[(properties_copy_df.ip == self.star)
                                                         & (properties_copy_df.field_name == field_name)]

        # step 3: filter by tenant
        if tenant_name != self.star:
            final_db = matching_properties_df[(matching_properties_df.tenant_name == tenant_name)
                      & (matching_properties_df.field_name == field_name)]
            if final_db.empty:
                final_db = matching_properties_df[(matching_properties_df.tenant_name == self.star) &
                          (matching_properties_df.field_name == field_name)]
        # step 4: filter for all tenants
        else:
            final_db = matching_properties_df[(matching_properties_df.tenant_name == self.star) &
                      (matching_properties_df.field_name == field_name)]

        if final_db.empty:
            return None
        else:
            return final_db.field_value.values[0]

    def load(self, ip, service_name):
        service_id = ConfigClient.__fetch_service_id(service_name)
        url = ConfigClient.__get_properties_url(service_id)
        response = requests.request("GET", url)

        if response.ok:
            self.properties = pd.DataFrame(response.json()['data'])

            field_names = self.properties.name.unique().tolist()
            final_properties = {}
            for field_name in field_names:
                val = self.__evaluate_value(field_name, self.star, ip)
                if val:
                    final_properties[field_name] = val

            return final_properties
        else:
            response.raise_for_status()

    def get(self, field_name, tenant_name='*', ip='*', default=None):
        value = self.__evaluate_value(field_name, tenant_name, ip)
        if not value:
            return default
        else:
            return value

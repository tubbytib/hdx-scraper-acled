#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Unit tests for acled.

"""
from os.path import join

import pytest
from hdx.data.vocabulary import Vocabulary
from hdx.hdx_configuration import Configuration
from hdx.hdx_locations import Locations
from hdx.location.country import Country

from acled import generate_dataset_and_showcase, get_countriesdata


class TestAcled():
    countrydata = {'m49': 120, 'iso3': 'CMR', 'countryname': 'Cameroon'}
    dataset = {'maintainer': '8b84230c-e04a-43ec-99e5-41307a203a2f', 'name': 'acled-data-for-cameroon',
               'dataset_date': '01/01/1997-12/31/2018', 'groups': [{'name': 'cmr'}],
               'tags': [{'name': 'hxl', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}, {'name': 'violence and conflict', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}, {'name': 'protests', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}, {'name': 'security incidents', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}],
               'owner_org': 'b67e6c74-c185-4f43-b561-0e114a736f19', 'data_update_frequency': '0',
               'title': 'Cameroon - Conflict Data', 'subnational': '1', 'dataset_preview': 'resource_id'}
    resource = {'description': 'Conflict data with HXL tags', 'name': 'Conflict Data for Cameroon',
                'format': 'csv', 'resource_type': 'api', 'url_type': 'api', 'dataset_preview_enabled': 'True',
                'url': 'https://proxy.hxlstandard.org/data/download/Conflict Data for Cameroon.csv?url=http%3A%2F%2Flala%3Fiso%3D120&name=ACLEDHXL&tagger-match-all=on&tagger-03-header=event_id_cnty&tagger-03-tag=%23event%2Bcode&tagger-05-header=event_date&tagger-05-tag=%23date%2Boccurred&tagger-06-header=year&tagger-06-tag=%23date%2Byear&tagger-08-header=event_type&tagger-08-tag=%23event%2Btype&tagger-09-header=actor1&tagger-09-tag=%23group%2Bname%2Bfirst&tagger-10-header=assoc_actor_1&tagger-10-tag=%23group%2Bname%2Bfirst%2Bassoc&tagger-12-header=actor2&tagger-12-tag=%23group%2Bname%2Bsecond&tagger-13-header=assoc_actor_2&tagger-13-tag=%23group%2Bname%2Bsecond%2Bassoc&tagger-16-header=region&tagger-16-tag=%23region%2Bname&tagger-17-header=country&tagger-17-tag=%23country%2Bname&tagger-18-header=admin1&tagger-18-tag=%23adm1%2Bname&tagger-19-header=admin2&tagger-19-tag=%23adm2%2Bname&tagger-20-header=admin3&tagger-20-tag=%23adm3%2Bname&tagger-21-header=location&tagger-21-tag=%23loc%2Bname&tagger-22-header=latitude&tagger-22-tag=%23geo%2Blat&tagger-23-header=longitude&tagger-23-tag=%23geo%2Blon&tagger-25-header=source&tagger-25-tag=%23meta%2Bsource&tagger-27-header=notes&tagger-27-tag=%23description&tagger-28-header=fatalities&tagger-28-tag=%23affected%2Bkilled&tagger-30-header=iso3&tagger-30-tag=%23country%2Bcode&header-row=1'}

    @pytest.fixture(scope='function')
    def configuration(self):
        Configuration._create(user_agent='test', hdx_key='12345',
                              project_config_yaml=join('tests', 'config', 'project_configuration.yml'))
        Locations.set_validlocations([{'name': 'afg', 'title': 'Afghanistan'}, {'name': 'cmr', 'title': 'Cameroon'}])
        Country.countriesdata(use_live=False)
        Vocabulary._tags_dict = True
        Vocabulary._approved_vocabulary = {'tags': [{'name': 'hxl'}, {'name': 'violence and conflict'}, {'name': 'protests'}, {'name': 'security incidents'}], 'id': '4e61d464-4943-4e97-973a-84673c1aaa87', 'name': 'approved'}

    @pytest.fixture(scope='function')
    def downloader(self):
        class Response:
            @staticmethod
            def json():
                pass

        class Download:
            @staticmethod
            def get_tabular_rows(url, dict_rows, headers, format=None):
                if url == 'http://haha':
                    return [{'Name': 'Cameroon', 'ACLED country-code': 'CMR', 'ISO Code': 120, 'Region-code': 'Middle Africa'}]
                elif url == 'http://lala?iso=120':
                    return [{'year': '1997'}, {'year': '2018'}]
                elif url == 'http://lala?iso=4':
                    return list()

        return Download()

    def test_get_countriesdata(self, downloader):
        countriesdata = get_countriesdata('http://haha', downloader)
        assert countriesdata == [TestAcled.countrydata]

    def test_generate_dataset_and_showcase(self, configuration, downloader):
        hxlproxy_url = Configuration.read()['hxlproxy_url']
        dataset, showcase = generate_dataset_and_showcase('http://lala?', hxlproxy_url, downloader, TestAcled.countrydata)
        assert dataset == TestAcled.dataset

        resources = dataset.get_resources()
        assert resources == [TestAcled.resource]

        assert showcase == {'name': 'acled-data-for-cameroon-showcase', 'notes': 'Conflict Data Dashboard for Cameroon',
                            'url': 'https://www.acleddata.com/dashboard/#120',
                            'tags': [{'name': 'hxl', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}, {'name': 'violence and conflict', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}, {'name': 'protests', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}, {'name': 'security incidents', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}],
                            'title': 'Dashboard for Cameroon', 'image_url': 'https://www.acleddata.com/wp-content/uploads/2018/01/dash.png'}

        dataset, showcase = generate_dataset_and_showcase('http://lala?', hxlproxy_url, downloader, {'m49': 4, 'iso3': 'AFG', 'countryname': 'Afghanistan'})
        assert dataset is None

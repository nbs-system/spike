import unittest
from time import time

from spike import create_app
from spike.model import db
from spike.model.naxsi_whitelist import NaxsiWhitelist

try:
    from urlparse import urlparse
except ImportError:  # python3
    from urllib.parse import urlparse


class FlaskrTestCase(unittest.TestCase):
    def setUp(self):
        app = create_app()
        db.init_app(app)
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.wid = self.__create_whitelist()

    def tearDown(self):
        db.session.delete(NaxsiWhitelist.query.filter(NaxsiWhitelist.id == self.wid).first())
        db.session.commit()

    @staticmethod
    def __create_whitelist():
        _wlist = NaxsiWhitelist(wl='wl:42', timestamp=int(time()), whitelistset='WORDPRESS', mz='BODY', active=1,
                                negative=False)
        db.session.add(_wlist)
        db.session.commit()
        return NaxsiWhitelist.query.order_by(NaxsiWhitelist.id.desc()).first().id

    def test_index(self):
        rv = self.app.get('/whitelists/')
        self.assertEqual(rv.status_code, 200)

    def test_plain(self):
        _id = NaxsiWhitelist.query.order_by(NaxsiWhitelist.id.desc()).first().id

        rv = self.app.get('/whitelists/plain/%d' % (_id + 1))
        self.assertEqual(rv.status_code, 302)

        rv = self.app.get('/whitelists/plain/%d' % _id)
        self.assertIn('BasicRule  wl:wl:42 "mz:BODY";', str(rv.data))

    def test_view(self):
        _id = NaxsiWhitelist.query.order_by(NaxsiWhitelist.id.desc()).first().id

        rv = self.app.get('/whitelists/view/%d' % (_id + 1))
        self.assertEqual(rv.status_code, 302)

    def test_del(self):
        wlist = NaxsiWhitelist(wl='wl:42', timestamp=int(time()), whitelistset='WORDPRESS', mz='BODY', active=1,
                               negative=False)
        db.session.add(wlist)
        db.session.commit()
        _id = NaxsiWhitelist.query.order_by(NaxsiWhitelist.id.desc()).first().id

        rv = self.app.get('/whitelists/del/%d' % (_id + 1))
        self.assertEqual(302, rv.status_code)

        rv = self.app.get('/whitelists/del/%d' % _id, follow_redirects=True)
        self.assertIn('Successfully deleted %d' % _id, str(rv.data))

    def test_new(self):
        rv = self.app.get('/whitelists/new')
        self.assertEqual(rv.status_code, 200)

        rv = self.app.post('/whitelists/new', data={'wl': '42',
                                                    'mz': 'BODY', 'whitelistset': 'WORDPRESS'})
        self.assertEqual(rv.status_code, 200)
        _wlist = NaxsiWhitelist.query.order_by(NaxsiWhitelist.id.desc()).first()
        self.assertEqual(_wlist.mz, 'BODY')
        self.assertEqual(_wlist.negative, 0)
        self.assertEqual(_wlist.wl, '42')

        rv = self.app.post('/whitelists/new', data={'mz': 'BODY', 'custom_mz_val': '', 'whitelistset': 'WORDPRESS'})
        self.assertIn('Please enter a wl', str(rv.data))
        rv = self.app.post('/whitelists/new', data={'mz': 'BODY', 'custom_mz_val': '', 'wl': '42'})
        self.assertIn('Please enter a whitelistset', str(rv.data))

        rv = self.app.post('/whitelists/new', data={'mz': 'BODY', 'custom_mz_val': '', 'wl': 'abcdef',
                                                    'whitelistset': 'WORDPRESS'}, follow_redirects=True)
        self.assertIn('Illegal character in the wl.', str(rv.data))

        db.session.delete(NaxsiWhitelist.query.order_by(NaxsiWhitelist.id.desc()).first())
        db.session.commit()

    def test_generate(self):
        rv = self.app.get('/whitelists/generate')
        self.assertEqual(rv.status_code, 200)

        rv = self.app.post('/whitelists/generate')
        self.assertEqual(rv.status_code, 200)
        self.assertIn('Please input nxlogs', str(rv.data))

        rv = self.app.post('/whitelists/generate', data={'nxlogs': 'pouet,lol'})
        self.assertEqual(rv.status_code, 200)
        self.assertIn('string &#34;ip=&#34; not found.', str(rv.data))

        rv = self.app.post('/whitelists/generate', data={'nxlogs': 'ip=1234'})
        self.assertEqual(rv.status_code, 200)
        self.assertIn('string &#34;,&#34; not found.', str(rv.data))

        logs = "2013/11/10 07:36:19 [error] 8278#0: *5932 NAXSI_FMT: ip=X.X.X.X&server=Y.Y.Y.Y&" \
               "uri=/phpMyAdmin-2.8.2/scripts/setup.php&learning=0&vers=0.52&total_processed=472&total_blocked=204&" \
               "block=0&cscore0=$UWA&score0=8&zone0=HEADERS&id0=42000227&var_name0=user-agent, client: X.X.X.X," \
               'server: blog.memze.ro, request: "GET /phpMyAdmin-2.8.2/scripts/setup.php HTTP/1.1", host: "X.X.X.X"'
        rv = self.app.post('/whitelists/generate', data={'nxlogs': logs})
        self.assertEqual(rv.status_code, 200)
        self.assertIn('BasicRule wl:42000227 "mz:$HEADERS_VAR:user-agent";', str(rv.data))

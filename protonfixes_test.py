# pylint: disable=C0114
import unittest
import os
import fix

# pylint: disable=C0115,R0904
class TestProtonfixes(unittest.TestCase):
    def setUp(self):
        self.env = {
            'STORE': '',
            'SteamAppId': '',
            'SteamGameId': '',
            'STEAM_COMPAT_DATA_PATH': '',
            'UMU_ID': ''
        }
        self.game_id = '1293820'
        self.pfx = Path(tempfile.mkdtemp())

    def tearDown(self):
        for key in self.env:
            if key in os.environ:
                os.environ.pop(key)

    def testModuleName(self):
        """Pass a non-numeric game id
        
        Expects a string that refers to a module in gamefixes-umu
        """
        game_id = 'umu-default'
        result = fix.get_module_name(game_id)
        self.assertEqual(result, 'protonfixes.gamefixes-umu.umu-default')

    def testModuleNameNum(self):
        """Pass a numeric game id
        
        In this case, it's assumed the game is from Steam when the game id is
        numeric
        Expects a string that refers to a module in gamefixes-steam
        """
        game_id = '1091500'
        result = fix.get_module_name(game_id)
        self.assertEqual(result, f'protonfixes.gamefixes-steam.{game_id}')

    def testModuleNameNoneAndNumeric(self):
        """Pass a numeric gameid and set STORE
        
        In this case, when the game id is numeric, we always refer to a
        module in the gamefixes-steam.
        """
        game_id = '1091500'
        os.environ['STORE'] = 'none'
        result = fix.get_module_name(game_id)
        self.assertEqual(result, f'protonfixes.gamefixes-steam.{game_id}')

    def testModuleNameStoreAndNumeric(self):
        """Pass a numeric gameid and set STORE
        
        In this case, when the game id is numeric, we always refer to a
        module in gamefixes-steam
        When passed a valid store, that value should not be used
        """
        game_id = '1091500'
        os.environ['STORE'] = 'gog'
        result = fix.get_module_name(game_id)
        self.assertEqual(result, f'protonfixes.gamefixes-steam.{game_id}')


    def testModuleNameStore(self):
        """Pass a non-numeric game id and setting valid STORE
        
        For non-numeric game ids, the umu database should always be referenced
        Expects a string that refers to a module in gamefixes-$STORE
        """
        os.environ['STORE'] = 'GOG'
        game_id = 'umu-1091500'
        result = fix.get_module_name(game_id)
        self.assertEqual(result, f'protonfixes.gamefixes-gog.{game_id}')

    def testModuleNameNoStore(self):
        """Pass a non-numeric game id and setting an invalid STORE
        
        Expects a string that refers to a module in gamefixes-umu
        """
        os.environ['STORE'] = 'foo'
        game_id = 'umu-1091500'
        result = fix.get_module_name(game_id)
        self.assertEqual(result, f'protonfixes.gamefixes-umu.{game_id}')

    def testModuleNameStoreEmpty(self):
        """Pass a non-numeric game id and setting an empty store
        
        Expects a string that refers to a module in gamefixes-umu
        """
        os.environ['STORE'] = ''
        game_id = 'umu-1091500'
        result = fix.get_module_name(game_id)
        self.assertEqual(result, f'protonfixes.gamefixes-umu.{game_id}')

    def testModuleNameEmpty(self):
        """Pass empty strings for the game id and store"""
        os.environ['STORE'] = ''
        game_id = ''
        result = fix.get_module_name(game_id)
        # TODO Handle the empty string case in fix.py
        # While umu enforces setting a gameid, it would still be a good idea
        # to handle this case
        self.assertEqual(result, 'protonfixes.gamefixes-umu.')

    def testModuleNameDefault(self):
        """Pass a gameid and default=True"""
        game_id = '1091500'
        result = fix.get_module_name(game_id, default=True)
        self.assertEqual(result, 'protonfixes.gamefixes-steam.default')

    def testModuleNameLocal(self):
        """Pass a gameid and local=True"""
        game_id = '1091500'
        result = fix.get_module_name(game_id, local=True)
        self.assertEqual(result, f'localfixes.{game_id}')

    def testModuleNameLocalDefault(self):
        """Pass a gameid and set local=True,default=True
        
        In this case, the game id will be completely ignored
        """
        game_id = '1091500'
        result = fix.get_module_name(game_id, local=True, default=True)
        self.assertEqual(result, 'localfixes.default')

    def testGetGameSteamAppId(self):
        """Only set the SteamAppId
        
        Protonfixes depends on being supplied an app id when applying fixes
        to games.
        
        This appid is typically set by a client application, but the user can
        set it in some cases (e.g., umu-launcher).
        
        If the app id is numeric, then protonfixes will refer to the
        gamefixes-steam folder. Otherwise, the STORE environment variable will
        be used to determine which fix will be applied.
        """
        os.environ['SteamAppId'] = self.game_id
        result = fix.get_game_id()
        self.assertEqual(result, self.game_id)
        self.assertTrue(os.environ.get('SteamAppId'), 'SteamAppId was unset')

    def testGetGameUmuId(self):
        """Only set the UMU_ID"""
        os.environ['UMU_ID'] = self.game_id
        result = fix.get_game_id()
        self.assertEqual(result, self.game_id)
        self.assertTrue(os.environ.get('UMU_ID'), 'UMU_ID was unset')

    def testGetGameSteamGameId(self):
        """Only set the SteamGameId"""
        os.environ['SteamGameId'] = self.game_id
        result = fix.get_game_id()
        self.assertEqual(result, self.game_id)
        self.assertTrue(os.environ.get('SteamGameId'), 'SteamGameId was unset')

    def testGetGameCompatPath(self):
        """Only set the STEAM_COMPAT_DATA_PATH"""
        os.environ['STEAM_COMPAT_DATA_PATH'] = self.game_id
        result = fix.get_game_id()
        self.assertEqual(result, self.game_id)
        self.assertTrue(os.environ.get('STEAM_COMPAT_DATA_PATH'), 'STEAM_COMPAT_DATA_PATH was unset')

    def testGetGameNone(self):
        """Set no environment variables
        
        Expect None to be returned
        """
        func = fix.get_game_id.__wrapped__  # Do not reference the cache
        self.assertTrue('STEAM_COMPAT_DATA_PATH' not in os.environ, 'STEAM_COMPAT_DATA_PATH is set')
        self.assertTrue('SteamGameId' not in os.environ, 'SteamGameId is set')
        self.assertTrue('UMU_ID' not in os.environ, 'UMU_ID is set')
        self.assertTrue('SteamAppId' not in os.environ, 'SteamAppId is set')
        result = func()
        self.assertFalse(result, 'None was not returned')
if __name__ == '__main__':
    unittest.main()

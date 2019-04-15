from Jumpscale import j
import onetimepass
from base64 import b32encode


JSBASE = j.application.JSBaseClass


class threebotsettings(JSBASE):
    def __init__(self):
        JSBASE.__init__(self)

        self._threebotsettings_model = None
        zdb_cl = j.clients.zdb.client_get(
            addr="0.0.0.0", port=9901, nsname="threefold")
        self._bcdb = j.data.bcdb.new(
            zdbclient=zdb_cl, name="threebotsettings")
        self._bcdb.models_add(
            "/sandbox/code/github/threefoldtech/digitalmeX/packages/threefold/schemas")

    # def connect(self, zdb_host, zdb_port, zdb_ns, schema_out):
    #     """
    #     ```in
    #     zdb_host = "0.0.0.0" (S)
    #     zdb_port = "9900" (S)
    #     zdb_ns = "threebotsettings" (S)
    #     ```
    #     """

    #     zdb_cl = j.clients.zdb.client_get(
    #         nsname=zdb_ns, addr=zdb_host, port=zdb_port)
    #     self._bcdb = j.data.bcdb.new(
    #         zdbclient=zdb_cl, name="threebotsettings_bcdb")
    #     self._bcdb.model_add(
    #         "/sandbox/code/github/threefoldtech/digitalmeX/packages/threefold/schemas/threefold_grid_threebotsettings.toml")

    @property
    def threebotsettings_model(self):
        if not self._threebotsettings_model:
            self._threebotsettings_model = self._bcdb.model_get(
                'threefold.grid.threebotsettings')
        return self._threebotsettings_model

    def get_otp(self, doubleName):
        if isinstance(doubleName, bytes):
            doubleName = doubleName.decode()
        if self._bcdb is None:
            raise RuntimeError("please connect to zdb first")

        bot_model = None
        threebots = self.threebotsettings_model.get_all()
        for bot in threebots:
            if bot.doubleName == doubleName:
                bot_model = bot
                break

        if bot_model:
            if not bot_model.totp_secret:
                secret = b32encode(
                    j.data.idgenerator.generateXCharID(8).encode())
                bot_model.totp_secret = secret
                bot_model.save()
            # j.shell()
            totp = onetimepass.get_totp(bot_model.totp_secret)
            return totp

        return False

    def get_threebotsettings(self, doubleName, schema_out):
        """
        ```in
        doubleName = (S)
        ```

        ```out
        !threefold.grid.threebotsettings
        ```
        """
        out = schema_out.new()
        threebots = self.threebotsettings_model.get_all()
        for bot in threebots:
            if bot.doubleName == doubleName:
                out = bot
                break

        # TODO: make sure u don't return the totp here
        out.totp_secret = ""
        return out._data

    def update_threebotsettings(self, doubleName, totp, firstName, lastName, email, addressStreet, addressNumber, addressZipcode, addressCity, addressCountry, telephone):
        """
        ```in
        doubleName = (S)
        totp = ""
        firstName* = ""
        lastName = ""                
        email* = ""         
        addressStreet = ""  
        addressNumber = ""
        addressZipcode = ""
        addressCity = ""                     
        addressCountry* = "" 
        telephone =
        ```
        """
        bot_model = None
        threebots = self.threebotsettings_model.get_all()
        for bot in threebots:
            if bot.doubleName == doubleName:
                bot_model = bot
                break

        if bot_model and onetimepass.valid_totp(totp, bot_model.totp_secret):
            bot_model.firstName = firstName
            bot_model.lastName = lastName
            bot_model.email = email
            bot_model.addressStreet = addressStreet
            bot_model.addressNumber = addressNumber
            bot_model.addressZipcode = addressZipcode
            bot_model.addressCity = addressCity
            bot_model.addressCountry = addressCountry
            bot_model.telephone = telephone

            bot_model.save()
            return True

        return False

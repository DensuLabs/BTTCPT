#!/usr/bin/python

import cmd, os, signal, getpass, time, HTMLParser
import libs.bt3in, libs.bt3out, libs.bt3ver, libs.bt3api
import modules.maligno, modules.mocksum, modules.pcapteller


class Menu(cmd.Cmd):

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.api_credentials = []
        self.hash_iterations = 50000
        self.maligno_menu = modules.maligno.Menu()
        self.mocksum_menu = modules.mocksum.Menu()
        self.pcapteller_menu = modules.pcapteller.Menu()


    def api_creds_preload(self, api_creds):
        self.api_credentials = api_creds
        self.maligno_menu.api_credentials = api_creds
        self.mocksum_menu.api_credentials = api_creds
        self.pcapteller_menu.api_credentials = api_creds


    def clear_api_creds(self):
        if len(self.api_credentials) == 2:
            self.api_credentials[0] = libs.bt3api.generate_string()
            self.api_credentials[1] = libs.bt3api.generate_string()
            self.api_credentials    = []

        if len(self.maligno_menu.api_credentials) == 2:
            self.maligno_menu.api_credentials[0] = libs.bt3api.generate_string()
            self.maligno_menu.api_credentials[1] = libs.bt3api.generate_string()
            self.maligno_menu.api_credentials    = []

        if len(self.mocksum_menu.api_credentials) == 2:
            self.mocksum_menu.api_credentials[0] = libs.bt3api.generate_string()
            self.mocksum_menu.api_credentials[1] = libs.bt3api.generate_string()
            self.mocksum_menu.api_credentials    = []

        if len(self.pcapteller_menu.api_credentials) == 2:
            self.pcapteller_menu.api_credentials[0] = libs.bt3api.generate_string()
            self.pcapteller_menu.api_credentials[1] = libs.bt3api.generate_string()
            self.pcapteller_menu.api_credentials    = []


    def complete_show(self, text, line, begidx, endidx):
        return [i for i in ["modules", "subscription"] if i.startswith(text)]


    def complete_use(self, text, line, begidx, endidx):
        return [i for i in ["maligno", "mocksum", "pcapteller"] if i.startswith(text)]


    def default(self, args):
        print("")
        libs.bt3out.print_error("%s\n" % libs.bt3out.INVALID_COMMAND)


    def do_apiconnect(self, args):
        try:
            print("")
            signal.signal(signal.SIGINT, libs.bt3in.allow_keyboard_interrupt)
            libs.bt3out.print_info("Please, enter your BT3 content subscription credentials (password not echoed)\n")
            api_username = raw_input("      E-mail: ")
            tmp_pwd = getpass.getpass("    Password: ")
            api_username = api_username.lower()
            api_password = libs.bt3api.hash_password(tmp_pwd, api_username, self.hash_iterations)
            tmp_pwd = libs.bt3api.generate_string()
            if api_username and api_password:
                self.api_creds_preload([api_username, api_password])
                json_results = libs.bt3api.get_welcome_info(api_username, api_password)
                if json_results and libs.bt3api.validate_json(json_results):
                    parsed_results = libs.bt3api.parse_json(json_results)
                    if parsed_results[-1]["Result"]:
                        del parsed_results[-1]
                        for welcomeInfo in parsed_results:
                            print("\n")
                            html_parser = HTMLParser.HTMLParser()
                            libs.bt3out.print_info("Hello %s, Welcome to the BT3 with API powers!" % html_parser.unescape(welcomeInfo["FirstName"]).encode("UTF-8"))

                            if welcomeInfo["LastLogin"] in ["0000-00-00 00:00:00"]:
                                libs.bt3out.print_info("Last login: Never")
                            else:
                                libs.bt3out.print_info("Last login: %s (UTC)" % welcomeInfo["LastLogin"])

                            if welcomeInfo["LastFailedLogin"] in ["0000-00-00 00:00:00"]:
                                libs.bt3out.print_info("Last failed login: Never\n")

                            else:
                                libs.bt3out.print_info("Last failed login: %s (UTC)\n" % welcomeInfo["LastFailedLogin"])

                    else:
                        print("")
                        self.clear_api_creds()
                        libs.bt3out.print_error("%s" % parsed_results[-1]["Msg"])
                        libs.bt3out.print_error("%s\n" % libs.bt3out.OFFLINE_MODE)

                else:
                    print("")
                    self.clear_api_creds()
                    libs.bt3out.print_error("%s" % libs.bt3out.API_INCOMMUNICATION)
                    libs.bt3out.print_error("%s\n" % libs.bt3out.CONTACT_SUPPORT)
                    libs.bt3out.print_error("%s\n" % libs.bt3out.OFFLINE_MODE)

            else:
                print("")
                self.clear_api_creds()
                libs.bt3out.print_error("%s\n" % libs.bt3out.OFFLINE_MODE)

            signal.signal(signal.SIGINT, libs.bt3in.prevent_keyboard_interrupt)

        except KeyboardInterrupt:
            self.clear_api_creds()
            signal.signal(signal.SIGINT, libs.bt3in.prevent_keyboard_interrupt)

        except Exception as e:
            print("")
            self.clear_api_creds()
            libs.bt3out.print_error("%s" % e)
            libs.bt3out.print_error("%s\n" % libs.bt3out.OFFLINE_MODE)


    def do_apidisconnect(self, args):
        self.clear_api_creds()
        print("")
        libs.bt3out.print_info("%s\n" % libs.bt3out.API_DISCONNECTED)


    def do_apinewcreds(self, args):
        api_username = ""
        api_new_pwd  = ""
        api_conf_pwd = ""
        try:
            signal.signal(signal.SIGINT, libs.bt3in.allow_keyboard_interrupt)
            os.system("clear")
            print("")
            libs.bt3out.print_info("You are about to set new credentials for your BT3 content subscription account.")
            libs.bt3out.print_info("A security code will be sent to your registered e-mail address during this process.\n")
            libs.bt3out.print_info("You may press [CTRL+C] to abort this new credentials request at any time.")
            libs.bt3out.print_info("If you do so, you may type 'apinewcreds' to restart this process.")
            print("")

            if args:
                api_username = args

            else:
                api_username = raw_input("         E-mail: ")

            if api_username:
                json_results = libs.bt3api.new_credentials_step_1(api_username)
                if json_results and libs.bt3api.validate_json(json_results):
                    parsed_results = libs.bt3api.parse_json(json_results)
                    if parsed_results[-1]["Result"]:
                        api_recovery_token = raw_input("    E-mail Code: ")

                        print("")
                        libs.bt3out.print_info("Processing...")
                        complex_pwd = False
                        matched_pwd = False
                        while not complex_pwd or not matched_pwd:
                            time.sleep(2.5)
                            os.system("clear")
                            print("")
                            libs.bt3out.print_info("It's time to choose a good password.")
                            libs.bt3out.print_info("%s" % libs.bt3out.PASSWORD_POLICY)
                            libs.bt3out.print_info("Passwords will not be echoed during this process.\n")
                            api_new_pwd  = getpass.getpass("    New Password: ")
                            api_conf_pwd = getpass.getpass("         Confirm: ")
                            print("")
                            if libs.bt3in.check_password_policy(api_new_pwd):
                                complex_pwd = True

                            else:
                                complex_pwd = False
                                libs.bt3out.print_error("%s" % libs.bt3out.WEAK_PASSWORD)

                            if api_new_pwd == api_conf_pwd:
                                matched_pwd = True

                            else:
                                matched_pwd = False
                                libs.bt3out.print_error("%s" % libs.bt3out.PASSWORD_NOT_MATCHED)

                        #Ready to submit new credentials
                        json_results = libs.bt3api.new_credentials_step_2(api_username, api_recovery_token, api_new_pwd, api_conf_pwd)
                        api_new_pwd = libs.bt3api.generate_string()
                        api_conf_pwd = libs.bt3api.generate_string()

                        if json_results and libs.bt3api.validate_json(json_results):
                            parsed_results = libs.bt3api.parse_json(json_results)
                            if parsed_results[-1]["Result"]:
                                print("")
                                libs.bt3out.print_ok("Your credentials were successfully updated.")
                                libs.bt3out.print_info("You may now type 'apiconnect' and log in with your account.\n")

                            else:
                                print("")
                                libs.bt3out.print_error("%s\n" % parsed_results[-1]["Msg"])

                        else:
                            print("")
                            libs.bt3out.print_error("%s" % libs.bt3out.API_INCOMMUNICATION)
                            libs.bt3out.print_error("%s\n" % libs.bt3out.CONTACT_SUPPORT)
                            libs.bt3out.print_error("%s\n" % libs.bt3out.RESET_CREDS_RESTART)

                    else:
                        print("")
                        libs.bt3out.print_error("%s\n" % parsed_results[-1]["Msg"])

                else:
                    print("")
                    libs.bt3out.print_error("%s" % libs.bt3out.API_INCOMMUNICATION)
                    libs.bt3out.print_error("%s\n" % libs.bt3out.CONTACT_SUPPORT)
                    libs.bt3out.print_error("%s\n" % libs.bt3out.RESET_CREDS_RESTART)


            else:
                print("")
                libs.bt3out.print_error("A valid e-mail address is required.\n")

            signal.signal(signal.SIGINT, libs.bt3in.prevent_keyboard_interrupt)
            api_new_pwd = libs.bt3api.generate_string()
            api_conf_pwd = libs.bt3api.generate_string()

        except KeyboardInterrupt:
            signal.signal(signal.SIGINT, libs.bt3in.prevent_keyboard_interrupt)
            api_new_pwd = libs.bt3api.generate_string()
            api_conf_pwd = libs.bt3api.generate_string()

        except Exception as e:
            print("")
            signal.signal(signal.SIGINT, libs.bt3in.prevent_keyboard_interrupt)
            api_new_pwd = libs.bt3api.generate_string()
            api_conf_pwd = libs.bt3api.generate_string()
            libs.bt3out.print_error("%s\n" % e)


    def do_apiredeem(self, args):
        if len(self.api_credentials) == 2:
            if len(args) == 64:
                try:
                    json_results = libs.bt3api.redeem_credit_voucher(self.api_credentials[0], self.api_credentials[1], args)
                    if json_results and libs.bt3api.validate_json(json_results):
                        parsed_results = libs.bt3api.parse_json(json_results)
                        if parsed_results[-1]["Result"]:
                            print("")
                            libs.bt3out.print_ok("%s" % libs.bt3out.VOUCHER_REDEEMED)
                            libs.bt3out.print_info("You can check your subscription status by typing 'show subscription'.\n")

                        else:
                            print("")
                            libs.bt3out.print_error("%s\n" % parsed_results[-1]["Msg"])

                    else:
                        print("")
                        libs.bt3out.print_error("%s" % libs.bt3out.API_INCOMMUNICATION)
                        libs.bt3out.print_error("%s\n" % libs.bt3out.CONTACT_SUPPORT)

                except Exception as e:
                    print("")
                    libs.bt3out.print_error("%s\n" % e)

            else:
                print("")
                libs.bt3out.print_error("%s\n" % libs.bt3out.INVALID_VOUCHER_CODE)

        else:
            print("")
            libs.bt3out.print_error("%s\n" % libs.bt3out.API_AUTHENTICATION)


    def do_apisignup(self, args):
        try:
            signal.signal(signal.SIGINT, libs.bt3in.allow_keyboard_interrupt)
            os.system("clear")
            print("")
            libs.bt3out.print_info("You are about to create a BT3 content subscription account.")
            libs.bt3out.print_info("Before doing so, you need to go through the steps described below.")
            libs.bt3out.print_info("You may press [CTRL+C] to abort this account registration at any time.")
            print("")
            print("    1. Terms and Conditions")
            print("       BT3 content subscription accounts are free, and they are bound to a license.")
            print("       You must read the terms and conditions listed at \033[1;32mhttps://www.bt3.no/terms-conditions\033[1;m")
            print("")
            print("    2. Privacy Policy")
            print("       Your name and e-mail address will be gathered during the registration process.")
            print("       Encripto AS will use this information as follows:")
            print("")
            print("       - To give you access to the BT3 content subscription service.")
            print("       - To be in touch with you, once you have become a user.")
            print("       - To send you information about BT3 updates and marketing (you may unsubscribe at any time).")
            print("")
            print("       You can read our complete privacy policy at \033[1;32mhttps://www.bt3.no/privacy-policy\033[1;m")
            print("")
            print("    3. Acceptance and Consent")
            consent = raw_input("       Do you agree with the terms and conditions, as well as with the privacy policy? [Y/N]: ")
            if consent in ["Y", "y"]:
                os.system("clear")
                print("")                
                libs.bt3out.print_info("What may I call you?\n")
                api_first_name   = raw_input("    First Name: ")
                api_last_name    = raw_input("     Last Name: ")

                os.system("clear")
                print("")
                libs.bt3out.print_info("Would you like to use a Personal or Enterprise content license?")
                libs.bt3out.print_info("Check \033[1;32mhttps://www.bt3.no/terms-conditions\033[1;m for more details.\n")
                api_license      = libs.bt3in.get_license_type("    License [P/E]: ")

                os.system("clear")
                print("")
                libs.bt3out.print_info("What is your e-mail address?")
                libs.bt3out.print_info("This will be used as your username and for account verification purposes.\n")
                api_username     = raw_input("    E-mail: ")

                if api_first_name and api_last_name and api_license and api_username:
                    json_results = libs.bt3api.register_account(api_first_name, api_last_name, api_license, api_username, consent)

                    if json_results and libs.bt3api.validate_json(json_results):
                        parsed_results = libs.bt3api.parse_json(json_results)
                        if parsed_results[-1]["Result"]:
                            print("")
                            libs.bt3out.print_ok("Your account has been successfully created!")
                            set_api_creds = libs.bt3in.get_confirmation("We will now proceed to verify your e-mail address and set your account credentials.", "INFO")
                            if set_api_creds:
                                self.do_apinewcreds(api_username)

                            else:
                                libs.bt3out.print_warning("Your BT3 content subscription account has been created, but it has not been verified.")
                                libs.bt3out.print_info("You can complete the account verification and set your credentials by typing 'apinewcreds' at any time.\n")

                        else:
                            print("")
                            libs.bt3out.print_error("%s\n" % parsed_results[-1]["Msg"])

                    else:
                        print("")
                        libs.bt3out.print_error("%s" % libs.bt3out.API_INCOMMUNICATION)
                        libs.bt3out.print_error("%s\n" % libs.bt3out.CONTACT_SUPPORT)

                else:
                    print("")
                    libs.bt3out.print_error("Valid user information must be provided.\n")

            else:
                print("")
                libs.bt3out.print_error("API account creation was cancelled.")
                libs.bt3out.print_error("The Blue Team Training Toolkit terms and conditions / privacy policy were not accepted.\n")


            signal.signal(signal.SIGINT, libs.bt3in.prevent_keyboard_interrupt)

        except KeyboardInterrupt:
            signal.signal(signal.SIGINT, libs.bt3in.prevent_keyboard_interrupt)

        except Exception as e:
            print("")
            signal.signal(signal.SIGINT, libs.bt3in.prevent_keyboard_interrupt)
            libs.bt3out.print_error("%s\n" % e)


    def do_apidelete(self, args):
        if len(self.api_credentials) == 2:
            if libs.bt3in.get_confirmation("%s\n" % libs.bt3out.ACCOUNT_DELETION, "WARN"):
                try:
                    json_results = libs.bt3api.delete_account(self.api_credentials[0], self.api_credentials[1])
                    if json_results and libs.bt3api.validate_json(json_results):
                        parsed_results = libs.bt3api.parse_json(json_results)
                        if parsed_results[-1]["Result"]:
                            print("")
                            self.clear_api_creds()
                            libs.bt3out.print_ok("%s" % libs.bt3out.ACCOUNT_DELETED)
                            libs.bt3out.print_info("%s\n" % libs.bt3out.API_DISCONNECTED)

                        else:
                            print("")
                            libs.bt3out.print_error("%s\n" % parsed_results[-1]["Msg"])

                    else:
                        print("")
                        libs.bt3out.print_error("%s" % libs.bt3out.API_INCOMMUNICATION)
                        libs.bt3out.print_error("%s\n" % libs.bt3out.CONTACT_SUPPORT)

                except Exception as e:
                    print("")
                    libs.bt3out.print_error("%s\n" % e)

        else:
            print("")
            libs.bt3out.print_error("%s\n" % libs.bt3out.API_AUTHENTICATION)


    def do_back(self, args):
        pass


    def do_bt3update(self, args):
        print("")
        libs.bt3out.print_info("Checking for updates...")

        try:
            json_results = libs.bt3api.check_current_version(libs.bt3ver.__version__)
            if json_results and libs.bt3api.validate_json(json_results):
                parsed_results = libs.bt3api.parse_json(json_results)
                if parsed_results[-1]["Result"]:
                    del parsed_results[-1]
                    for updateInfo in parsed_results:
                        if float(updateInfo["CurrentVersion"]) > float(libs.bt3ver.__version__):
                            if libs.bt3in.get_confirmation("Blue Team Training Toolkit v%s is available for download.\n    %s\n" % (updateInfo["CurrentVersion"], libs.bt3out.BT3_INSTALL_UPDATE), "OK"):
                                libs.bt3ver.deploy_update(updateInfo["URL"], updateInfo["FileChecksum"], updateInfo["CurrentVersion"])

                        else:
                            print("")
                            libs.bt3out.print_info("%s\n" % libs.bt3out.BT3_LATEST_VERSION)

                else:
                    print("")
                    libs.bt3out.print_error("%s\n" % parsed_results[-1]["Msg"])

            else:
                print("")
                libs.bt3out.print_error("%s\n" % libs.bt3out.BT3_COULD_NOT_UPDATE)

        except Exception as e:
            print("")
            libs.bt3out.print_error("%s\n" % e)


    def do_exit(self, args):
        self.clear_api_creds()
        libs.bt3out.exit_program(args)


    def do_help(self, args):
        cmds = [["apiconnect", "Connect to Blue Team Training Toolkit API with valid credentials."],
                ["apidelete", "Delete your Blue Team Training Toolkit content subscription account."],
                ["apidisconnect", "Disconnect from Blue Team Training Toolkit API, and work in offline mode."],
                ["apinewcreds", "Start a Blue Team Training Toolkit API password change or account recovery."],
                ["apiredeem <code>", "Redeem a Blue Team Training Toolkit credit voucher."],
                ["apisignup", "Create a new Blue Team Training Toolkit content subscription account."],
                ["back", "Exit current selected module and return to main menu."],
                ["bt3update", "Check for software updates."],
                ["exit", "Exit the Blue Team Training Toolkit."],
                ["help", "Display help menu."],
                ["resource <file>", "Run a sequence of Blue Team Training Toolkit commands from a resource file."],
                ["show modules", "Display supported application modules."],
                ["show subscription", "Display Blue Team Training Toolkit content subscription details."],
                ["use <module>", "Select an application module."],
                ["version", "Display software version."]]
        libs.bt3out.print_help(cmds, False, True)


    def do_resource(self, args):
        args = args.split(" ")
        if len(args) == 1 and args[0] not in [""]:
            try:
                if libs.bt3in.check_file_exists(args[0]):
                    cmd_list = []
                    cmd_list_menu = []
                    print("")
                    libs.bt3out.print_info("Running resource file...")
                    res_file = open(args[0], "r")
                    for line in res_file:
                        line = line.replace("\n", "")
                        if len(line) > 0:
                            cmd_list.append(line)

                    res_file.close()

                    module_reached = False
                    for cmd in cmd_list:
                        if not module_reached:
                            cmd_list_menu.append(cmd)
                            if cmd.upper() in ["USE MALIGNO", "USE MOCKSUM", "USE PCAPTELLER"]:
                                module_reached = True

                        else:
                            if cmd_list_menu[-1].upper() in ["USE MALIGNO"]:
                                self.maligno_menu.resource_cmds.append(cmd)
                                if cmd.upper() in ["BACK"]:
                                    libs.bt3out.print_warning("%s" % libs.bt3out.LIMIT_RESOURCE_FILE)
                                    libs.bt3out.print_warning("%s" % libs.bt3out.IGNORE_RESOURCE_FILE)
                                    break

                            elif cmd_list_menu[-1].upper() in ["USE MOCKSUM"]:
                                self.mocksum_menu.resource_cmds.append(cmd)
                                if cmd.upper() in ["BACK"]:
                                    libs.bt3out.print_warning("%s" % libs.bt3out.LIMIT_RESOURCE_FILE)
                                    libs.bt3out.print_warning("%s" % libs.bt3out.IGNORE_RESOURCE_FILE)
                                    break

                            elif cmd_list_menu[-1].upper() in ["USE PCAPTELLER"]:
                                self.pcapteller_menu.resource_cmds.append(cmd)
                                if cmd.upper() in ["BACK"]:
                                    libs.bt3out.print_warning("%s" % libs.bt3out.LIMIT_RESOURCE_FILE)
                                    libs.bt3out.print_warning("%s" % libs.bt3out.IGNORE_RESOURCE_FILE)
                                    break
                    print("")
                    for cmd in cmd_list_menu:
                        c = self.precmd(cmd)
                        e = self.onecmd(c)

                else:
                    print("")
                    libs.bt3out.print_error("%s\n" % libs.bt3out.INVALID_RESOURCE_FILE)

            except Exception as e:
                print("")
                libs.bt3out.print_error("%s\n" % e)

        else:
            cmds = [["resource <file>", "Run a sequence of BT3 commands from a resource file."]]
            libs.bt3out.print_help(cmds, True, True)


    def do_show(self, args):
        if args.upper() in ["MODULES"]:
            cmds = [["maligno", "Attack simulation with customized malware indicators."],
                    ["mocksum", "Repository of harmless files mimicking malware samples via hash collisions."],
                    ["pcapteller", "Network traffic manipulation and replay."]]
            libs.bt3out.print_help(cmds, False, False)

        elif args.upper() in ["SUBSCRIPTION"]:
            if len(self.api_credentials) == 2:
                try:
                    json_results = libs.bt3api.get_subscription(self.api_credentials[0], self.api_credentials[1])
                    if json_results and libs.bt3api.validate_json(json_results):
                        parsed_results = libs.bt3api.parse_json(json_results)
                        if parsed_results[-1]["Result"]:
                            del parsed_results[-1]
                            for subscription in parsed_results:
                                libs.bt3out.print_subscription_details(subscription)

                        else:
                            print("")
                            libs.bt3out.print_error("%s\n" % parsed_results[-1]["Msg"])

                    else:
                        print("")
                        libs.bt3out.print_error("%s" % libs.bt3out.API_INCOMMUNICATION)
                        libs.bt3out.print_error("%s\n" % libs.bt3out.CONTACT_SUPPORT)

                except Exception as e:
                    print("")
                    libs.bt3out.print_error("%s\n" % e)

            else:
                print("")
                libs.bt3out.print_error("%s\n" % libs.bt3out.API_AUTHENTICATION)

        else:
            cmds = [["show modules", "Display supported application modules."],
                    ["show subscription", "Display BT3 content subscription details."]]
            libs.bt3out.print_help(cmds, True, True)


    def do_use(self, args):
        if args.upper() in ["MALIGNO"]:
            self.maligno_menu.prompt = libs.bt3out.print_prompt("maligno")
            self.maligno_menu.cmdloop()

        elif args.upper() in ["MOCKSUM"]:
            self.mocksum_menu.prompt = libs.bt3out.print_prompt("mocksum")
            self.mocksum_menu.cmdloop()

        elif args.upper() in ["PCAPTELLER"]:
            self.pcapteller_menu.prompt = libs.bt3out.print_prompt("pcapteller")
            self.pcapteller_menu.cmdloop()

        else:
            cmds = [["use maligno", "Use maligno module."],
                    ["use mocksum", "Use mocksum module."],
                    ["use pcapteller", "Use pcapteller module."]]
            libs.bt3out.print_help(cmds, True, True)


    def do_version(self, args):
        print("")
        libs.bt3out.print_info("You are running %s version %s\n" % ("Blue Team Training Toolkit (BT3)", libs.bt3ver.__version__))


    def emptyline(self):
        pass






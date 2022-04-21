# Standard Library imports
import socket, ssl, datetime, threading, time, sys, subprocess

try:
    import requests
    import msmcauth
    import fade
    from colorama import Fore
    from discord_webhook import DiscordWebhook, DiscordEmbed

except ImportError:
    print("Installing dependencies... (requirements.txt)")

    # sys.executable -m pip install -r requirements.txt (silenced stdout)
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], stderr=subprocess.STDOUT, stdout=subprocess.DEVNULL)
    
    # import again
    import requests
    import msmcauth
    import fade
    from colorama import Fore
    from discord_webhook import DiscordWebhook, DiscordEmbed

WEBHOOK_URL = ""
accdata = []
output = []
times = []
receive = []

def nameChangeAllowed(bearer) -> bool:
    try:
        return requests.get(
            "https://api.minecraftservices.com/minecraft/profile/namechange",
            headers={"Authorization": "Bearer " + bearer},
        ).json()["nameChangeAllowed"]
    except requests.exceptions.JSONDecodeError:
        return False

def auto_ping(number_of_pings):
    delays = []
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as so:
        so.connect(('api.minecraftservices.com', 443))
        context = ssl.create_default_context()
        ssock = context.wrap_socket(
            so, server_hostname='api.minecraftservices.com')
        for _ in range(number_of_pings):
            start = time.time()
            ssock.send(bytes(
                "PUT /minecraft/profile/name/TEST HTTP/1.1\r\nHost: api.minecraftservices.com\r\nAuthorization: Bearer " + "TEST_TOKEN\r\n\r\n",
                "utf-8"))
            ssock.recv(10000).decode('utf-8')
            delays.append(time.time() - start)
    return (sum(delays) / len(delays) * 1000 / 2)

def countdown_time(count):
    for i in range(int(count), 0, -1):
        minutes, seconds = divmod(i, 60)
        if minutes > 59:
            hours, minutes = divmod(minutes, 60)
            print(f"Generating Connection & Threads 😴 ~~ {'0' if hours < 10 else ''}{hours}:{'0' if minutes < 10 else ''}{minutes}:{'0' if seconds < 10 else ''}{seconds}", end="\r")
        elif minutes:
            print(f"Generating Connection & Threads 😫 ~~ {'0' if minutes < 10 else ''}{minutes}:{'0' if seconds < 10 else ''}{seconds}   ", end="\r")
        else:
            print(f"Generating Connection & Threads 👀 ~~ {seconds}s   ", end="\r")

        time.sleep(1)

# Check acc type
def isGC(bearer) -> bool:
    return requests.get("https://api.minecraftservices.com/minecraft/profile/namechange",
                       headers={"Authorization": f"Bearer {bearer}"}).status_code == 404

# EP Requests
def req(acc_payload):
    """Send Socket Payload"""
    times.append(time.time())
    ss.send(acc_payload)

def term_threads() -> None:
        threads = threading.active_count() - 1
        while threads:
            threads = threading.active_count() - 1
            sleep(0.5)  # Wait until threads terminate

# On Success
def success_true(token_list):
    for outs in output:
        if (status_code := outs["status"]) and int(status_code) == 200:
            print(f"{datetime.datetime.utcfromtimestamp(outs['times']).strftime('%S.%f')} @ [{Fore.GREEN}{status_code}{Fore.RESET}] ~ {datetime.datetime.utcfromtimestamp(outs['travel']).strftime('%S.%f')}")
            for token in token_list:
                headers = {"Authorization": f"Bearer {token['bearer']}"}
                username = requests.get(
                    "https://api.minecraftservices.com/minecraft/profile",
                    headers=headers,
                ).json()["name"]
                if username == target_name:
                    print(f"🎉 Sniped {Fore.MAGENTA}{target_name}{Fore.RESET} 🎉")
                    skin_change = requests.post(
                        "https://api.minecraftservices.com/minecraft/profile/skins",
                        json={
                            "variant": "classic",
                            "url": "https://i.imgur.com/8nuxlIk.png",
                        },
                        headers=headers,
                    )
                    if skin_change.status_code == 200:
                        print(f"{Fore.MAGENTA}Successfully delivered skin change{Fore.RESET}")
                    else:
                        print(f"{Fore.YELLOW}Failed to deliver skin change{Fore.RESET}")
            try:
                webhook = DiscordWebhook(url=WEBHOOK_URL, rate_limit_retry=True)
                embed = DiscordEmbed(title="NameMC", url=f'https://namemc.com/search?q={target_name}',
                                     description=f"**Sniped `{target_name}` :ok_hand:**", color=12282401)
                embed.set_thumbnail(
                        url='https://cdn.discordapp.com/icons/944338449140420690/eaf9e293982fe84b1bb5ff08f40a17f9.webp?size=1024')
                webhook.add_embed(embed)
                webhook.execute()
                print(f"{Fore.MAGENTA}Successfully executed webhook{Fore.RESET}")
            except requests.exceptions.MissingSchema:
                print(f"{Fore.YELLOW}No webhook url specified{Fore.RESET}")
            except requests.exceptions.ConnectionError:
                print(f"{Fore.YELLOW}Failed to execute webhook{Fore.RESET}")
        else:
            print(f"{datetime.datetime.utcfromtimestamp(outs['times']).strftime('%S.%f')} @ [{Fore.RED}{status_code}{Fore.RESET}] ~ {datetime.datetime.utcfromtimestamp(outs['travel']).strftime('%S.%f')}")  

def done(byt):
    term_threads()
    for sendrg in times:
        revs = ss.recv(byt).decode('utf-8')[9:12]
        time_end = time.time()
        receive.append({"exec": time_end - sendrg, "code": revs})
    print(receive)
    ss.close()
    output.extend([{"status": stats['code'], "times": None, "travel": stats['exec']} for stats in receive])
    [o.update({'times':tim, 'travel': tim + o['travel']}) or o for o,tim in zip(output, times)]
    success_true(accdata)

if __name__ == "__main__":
    try:
        # remove duplicates               
        with open("accs.txt", "r+") as file:
            accs = "\n".join(set(file.read().splitlines()))
            file.seek(0)
            file.truncate()
            file.write(accs)

        # Start main
        print(fade.purplepink(f"""
  ___       _                 _     
 / _ \     | |               (_)    
/ /_\ \_ __| |_ ___ _ __ ___  _ ___ 
|  _  | '__| __/ _ \ '_ ` _ \| / __|
| | | | |  | ||  __/ | | | | | \__ \\
\_| |_/_|   \__\___|_| |_| |_|_|___/                           
                        a r t e m i s"""))

        print("Blessed by the Goddess - Artemis\n")

        target_name = input("% Name ~> ")
        while not target_name:
            target_name = input("% Name ~> ")

        auto_offset = auto_ping(5)

        offset = float(input(f"\n% Offset [{auto_offset:.2f}ms] ~> ") or auto_offset)

        droptime = requests.get(f"http://api.star.shopping/droptime/{target_name}", headers={"User-Agent": "Sniper"}).json()

        if droptime.get("unix"):
            droptime = droptime["unix"] - (offset / 1000)
        else:
            print(f"\n{Fore.RED}ERROR: \"{droptime['error'].capitalize()}\"{Fore.RESET}")
            droptime = input(f"\n% {target_name} Unix Droptime ~> {Fore.RESET}")
            while not droptime:
                droptime = input(f"\n% {target_name} Unix Droptime ~> {Fore.RESET}")

            droptime = int(droptime)

        with open("accs.txt") as file:
            for line in file.read().splitlines():
                if not line.strip():
                    continue
                splitter = line.split(":")
                if len(splitter) != 2:
                    print(f"{Fore.LIGHTYELLOW_EX}Invalid account ~ \"{line}\"{Fore.RESET}")
                    continue
                
                email, password = splitter
                
                try:
                    if (msresp := msmcauth.login(email, password).access_token) and isGC(msresp):
                        # Gc auth
                        print(f"Authenticated {Fore.MAGENTA}{email}{Fore.RESET} ~ [GC]")
                        accdata.append({"reqamount": 2, "bearer": msresp,
                                        "payload": f"POST /minecraft/profile HTTP/1.1\r\nHost: api.minecraftservices.com\r\nprofileName: {target_name}\r\nAuthorization: Bearer {msresp}".encode()})
                    else:
                        # Microsoft auth
                        if not nameChangeAllowed(msresp):
                            print(f"{Fore.YELLOW}{email} cannot namechange{Fore.RESET}")
                            continue

                        accdata.append({"reqamount": 4, "bearer": msresp,
                                            "payload": f"PUT /minecraft/profile/name/{target_name} HTTP/1.1\r\nHost: api.minecraftservices.com\r\nAuthorization: Bearer {msresp}".encode()})
                        print(f"Authenticated {Fore.MAGENTA}{email}{Fore.RESET} ~ [MS]")
                except:
                    # Mojang auth
                    auth = requests.post("https://authserver.mojang.com/authenticate",
                                          json={"username": email, "password": password})
                    try:
                        auth_result = auth.json()
                        if auth.status_code == 200 and auth_result:
                            if not nameChangeAllowed(auth_result['accessToken']):
                                print(f"{Fore.YELLOW}{email} cannot namechange{Fore.RESET}")
                                continue

                            accdata.append({"reqamount": 4, "bearer": auth_result['accessToken'],
                                                "payload": f"PUT /minecraft/profile/name/{target_name} HTTP/1.1\r\nHost: api.minecraftservices.com\r\nAuthorization: Bearer {auth_result['accessToken']}".encode()})
                            print(f"Authenticated {Fore.MAGENTA}{email}{Fore.RESET} ~ [MJ]")
                        else:
                            raise Exception
                    except:
                        print(f"{Fore.YELLOW}[{auth.status_code}] ~ {email} failed to authenticate{Fore.RESET}")

        if not accdata:
            sys.exit(f"{Fore.RED}No accounts valid...{Fore.RESET}")

        # Prepare Sleep
        try:
            countdown_time((droptime - time.time()) - 8)
        except ValueError:
            pass
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('api.minecraftservices.com', 443))
        ss = ssl.create_default_context().wrap_socket(s, server_hostname='api.minecraftservices.com')
        #Generating Threads Before Droptime
        threads = []
        for acc_data in accdata:
            threads.extend([threading.Thread(target=req, args=(acc_data['payload'],)) for _ in range(acc_data.get("reqamount"))])
            
        time.sleep(droptime - time.time())
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        done(2046)

    finally:
        input("\nPress enter to exit...")

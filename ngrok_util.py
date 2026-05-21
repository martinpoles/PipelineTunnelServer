import subprocess
import time
import requests
from config import NGROK_PATH, PORT
import os 

NGROK_PROCESS = None

def start_ngrok():

    global NGROK_PROCESS

    print("\n================ NGROK START =================")

    print(f"[NGROK] cwd: {os.getcwd()}")
    print(f"[NGROK] path: {NGROK_PATH}")
    print(f"[NGROK] exists: {os.path.exists(NGROK_PATH)}")
    print(f"[NGROK] executable: {os.access(NGROK_PATH, os.X_OK)}")

    try:

        print("[NGROK] launching subprocess...")

        NGROK_PROCESS = subprocess.Popen(
            [NGROK_PATH, "http", str(PORT)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            text=True
        )

        print(f"[NGROK] pid: {NGROK_PROCESS.pid}")

    except Exception as e:

        print(f"[NGROK][FATAL] subprocess failed: {e}")
        raise


    time.sleep(3)

    poll = NGROK_PROCESS.poll()

    print(f"[NGROK] poll after startup: {poll}")

    if poll is not None:

        print("[NGROK][ERROR] process terminated immediately")

        try:
            out, err = NGROK_PROCESS.communicate(timeout=2)

            print(f"[NGROK][STDOUT]\n{out}")
            print(f"[NGROK][STDERR]\n{err}")

        except Exception as e:
            print(f"[NGROK] cannot read pipes: {e}")

        raise Exception("ngrok crashed immediately")

    url = None

    for i in range(30):

        print(f"[NGROK] polling localhost api attempt {i+1}/30")

        poll = NGROK_PROCESS.poll()

        if poll is not None:

            print(f"[NGROK][ERROR] process died during polling: {poll}")

            try:
                out, err = NGROK_PROCESS.communicate(timeout=2)

                print(f"[NGROK][STDOUT]\n{out}")
                print(f"[NGROK][STDERR]\n{err}")

            except Exception as e:
                print(f"[NGROK] cannot read pipes: {e}")

            raise Exception("ngrok terminated")

        try:

            res = requests.get(
                "http://localhost:4040/api/tunnels",
                timeout=2
            )

            print(f"[NGROK] localhost status: {res.status_code}")
            print(f"[NGROK] localhost body: {res.text}")

            tunnels = res.json().get("tunnels", [])

            print(f"[NGROK] tunnels found: {len(tunnels)}")

            if tunnels:

                candidate = tunnels[0]["public_url"]

                print(f"[NGROK] candidate url: {candidate}")

                try:

                    test = requests.get(
                        candidate + "/docs",
                        timeout=5
                    )

                    print(f"[NGROK] public test status: {test.status_code}")

                    if test.status_code in [200, 404]:

                        url = candidate

                        print("[NGROK] tunnel validated")

                        break

                except Exception as e:

                    print(f"[NGROK] public test failed: {e}")

        except Exception as e:

            print(f"[NGROK] localhost polling failed: {e}")

        time.sleep(1)

    if not url:

        print("[NGROK][FATAL] tunnel not stable")

        try:

            poll = NGROK_PROCESS.poll()

            print(f"[NGROK] final poll: {poll}")

            if poll is not None:

                out, err = NGROK_PROCESS.communicate(timeout=2)

                print(f"[NGROK][FINAL STDOUT]\n{out}")
                print(f"[NGROK][FINAL STDERR]\n{err}")

        except Exception as e:

            print(f"[NGROK] final debug failed: {e}")

        raise Exception("[NGROK] tunnel non stabile")

    print(f"[NGROK] URL READY: {url}")
    print("================ NGROK END =================\n")

    return url

def stop_ngrok():

    global NGROK_PROCESS

    if NGROK_PROCESS:
        NGROK_PROCESS.terminate()
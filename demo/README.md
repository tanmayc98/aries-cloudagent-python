

### Running in a Browser

In your browser, go to the [docker playground service](https://labs.play-with-docker.com/). On the title screen, click "Start". On the next screen, click (in the left menu) "+Add a new instance".  That will start up a terminal in your browser.

Run the following commands to start the Faber (Company1) agent:

```bash
git clone https://github.com/tanmayc98/aries-cloudagent-python
cd aries-cloudagent-python/demo
LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run_demo faber
```

Now to start Alice's agent. Click the "+Add a new instance" button again to open another terminal session. Run the following commands to start Alice's agent:

```bash
git clone https://github.com/tanmayc98/aries-cloudagent-python
cd aries-cloudagent-python/demo
LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run_demo alice
```

Alice's agent is now running.

For Acme (Company2) Agent, Click the "+Add a new instance" button again to open another terminal session.
```bash
git clone https://github.com/tanmayc98/aries-cloudagent-python
cd aries-cloudagent-python/demo
LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run_demo acme
```

Jump to the [Follow the Script](#follow-the-script) section below for further instructions.



### Follow The Script

With both the Alice and Faber agents started, go to the Faber terminal window. The Faber agent has created and displayed an invitation. Copy this invitation and paste it at the Alice prompt. The agents will connect and then show a menu of options:

Faber:

```
    1 = Issue Credential - send a credential to Alice
    2 = Send Proof Request - send a proof request to Alice
    3 = Send Message - send a message to Alice
    x = Exit - Stop and exit
```

Alice:

```
    3 = Send Message - send a message
    4 = Input New Invitation
    x = Exit - stop and exit
```

Go to the Company prompt, enter "1" to send a credential, and then "2" to request a proof.



Acme:

```
    1 = Issue Credential - send a credential to Alice
    2 = Send Proof Request - send a proof request to Alice
    3 = Send Message - send a message to Alice
    x = Exit - Stop and exit
    
    
    
Go to Faber, issue ex_employee schema credential(1). Open Acme in another container - send the proof request(2) and then issue the credential(1)

You should be able to see each credential issued.



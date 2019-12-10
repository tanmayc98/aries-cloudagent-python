import asyncio
import json
import logging
import os
import random
import sys

from uuid import uuid4

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # noqa

from runners.support.agent import DemoAgent, default_genesis_txns
from runners.support.utils import (
    log_json,
    log_msg,
    log_status,
    log_timer,
    prompt,
    prompt_loop,
    require_indy,
)
LOGGER = logging.getLogger(__name__)

#AGENT_PORT = int(sys.argv[1])

#TIMING = False

CRED_PREVIEW_TYPE = (
    "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview"
)


class AcmeAgent(DemoAgent):
    def __init__(self, http_port: int, admin_port: int, **kwargs):
        super().__init__("Acme Agent", http_port, admin_port, prefix="Acme", 
                        extra_args=["--auto-accept-invites", "--auto-accept-requests"],
                        **kwargs)
        self.connection_id = None
        self._connection_ready = asyncio.Future()
        self.cred_state = {}
        # TODO define a dict to hold credential attributes based on credential_definition_id
        self.cred_attrs = {}

    async def detect_connection(self):
        await self._connection_ready

    @property
    def connection_ready(self):
        return self._connection_ready.done() and self._connection_ready.result()

    async def handle_connections(self, message):
        if message["connection_id"] == self.connection_id:
            if message["state"] == "active" and not self._connection_ready.done():
                self.log("Connected")
                self._connection_ready.set_result(True)

    async def handle_issue_credential(self, message):
        state = message["state"]
        credential_exchange_id = message["credential_exchange_id"]
        prev_state = self.cred_state.get(credential_exchange_id)
        if prev_state == state:
            return  # ignore
        self.cred_state[credential_exchange_id] = state

        self.log(
            "Credential: state =",
            state,
            ", credential_exchange_id =",
            credential_exchange_id,
        )

        if state == "request_received":
            # TODO handle received credential requests
            log_status("#17 Issue credential to X")

            # TODO issue credentials based on the credential_definition_id
            cred_attrs = self.cred_attrs[message["credential_definition_id"]]
            cred_preview = {
                "@type": CRED_PREVIEW_TYPE,
                "attributes": [
                    {"name": n, "value": v} for (n, v) in cred_attrs.items()
                ],
            }
            await self.admin_POST(
                f"/issue-credential/records/{credential_exchange_id}/issue",
                {
                    "comment": f"Issuing credential, exchange {credential_exchange_id}",
                    "credential_preview": cred_preview,
                },
            )

    async def handle_present_proof(self, message):
        state = message["state"]

        presentation_exchange_id = message["presentation_exchange_id"]
        self.log(
            "Presentation: state =",
            state,
            ", presentation_exchange_id =",
            presentation_exchange_id,
        )

        if state == "presentation_received":
            # TODO handle received presentations

            # TODO if proof of student id, then validate
            log_status("#27 Process the proof provided by X")
            log_status("#28 Check if proof is valid")
            self.log("Presentation received:", json.dumps(message))
            proof = await self.admin_POST(
                f"/present-proof/records/{presentation_exchange_id}/"
                "verify_presentation"
            )
            self.log("Proof =", proof["verified"])
            self.log(message['presentation_request']['name'])

            # TODO if presentation is a degree schema (proof of education), also ask for proof of student id
           ''' is_proof_of_education = (message['presentation_request']['name'] == 'Proof of Education')
            if is_proof_of_education:
                log_status("#28.1 Received proof of education, now check for proof of student id")
                requested_student_id = None
                for attr, value in message['presentation_request']['requested_attributes'].items():
                    if value['name'] == 'student_id':
                        requested_student_id = message['presentation']['requested_proof']['revealed_attrs'][attr]['raw']
                proof_attrs = [
                    {"name": "student_id", "restrictions": [{"schema_name": "student id schema"}]},
                    {"name": "name", "restrictions": [{"schema_name": "student id schema"}]}, #, "attr::student_id::value": requested_student_id}]},
                    {"name": "program", "restrictions": [{"schema_name": "student id schema"}]}, #, "attr::student_id::value": requested_student_id}]},
                    {"name": "effective_date", "restrictions": [{"schema_name": "student id schema"}]}, #, "attr::student_id::value": requested_student_id}]},
                ]
                proof_predicates = []
                proof_request = {
                    "name": "Proof of Student ID",
                    "version": "1.0",
                    "connection_id": self.connection_id,
                    "requested_attributes": proof_attrs,
                    "requested_predicates": proof_predicates,
                }
                await self.admin_POST(
                    "/presentation_exchange/send_request", proof_request
                )
            else:
                self.log("#28.1 Received ", message['presentation_request']['name'])

            pass'''

    async def handle_basicmessages(self, message):
        self.log("Received message:", message["content"])


async def main(start_port: int, show_timing: bool = False):

    genesis = await default_genesis_txns()
    if not genesis:
        print("Error retrieving ledger genesis transactions")
        sys.exit(1)

    agent = None
    #start_port = AGENT_PORT

    try:
        log_status("#1 Provision an agent and wallet, get back configuration details")
        agent = AcmeAgent(start_port, start_port + 1, genesis_data=genesis, timing=show_timing)
        await agent.listen_webhooks(start_port + 2)
        await agent.register_did()

        with log_timer("Startup duration:"):
            await agent.start_process()
        log_msg("Admin url is at:", agent.admin_url)
        log_msg("Endpoint url is at:", agent.endpoint)

        # Create a schema
        log_status("#3 Create a new schema on the ledger")
        with log_timer("Publish schema duration:"):
            version = format(
                "%d.%d.%d"
                % (
                    random.randint(1, 101),
                    random.randint(1, 101),
                    random.randint(1, 101),
                )
            )
            # TODO define schema
            (schema_id, credential_definition_id) = await agent.register_schema_and_creddef(
                "employee id schema", version, ["employee_id", "name", "date", "position"]
                )
'''
        log_status("#3 Create a new schema on the ledger")
        with log_timer("Publish schema duration:"):
            version_2 = format(
                "%d.%d.%d"
                % (
                    random.randint(1, 101),
                    random.randint(1, 101),
                    random.randint(1, 101),
                )
            )
            # TODO define schema
            (schema_id_2, credential_definition_id_2) = await agent.register_schema_and_creddef(
                "income schema", version_2, ["employee_id", "name", "date", "salary"]
                )
'''
        with log_timer("Generate invitation duration:"):
            # Generate an invitation
            log_status(
                "#5 Create a connection to alice and print out the invite details"
            )
            connection = await agent.admin_POST("/connections/create-invitation")

        agent.connection_id = connection["connection_id"]
        log_json(connection, label="Invitation response:")
        log_msg("*****************")
        log_msg(json.dumps(connection["invitation"]), label="Invitation:", color=None)
        log_msg("*****************")

        log_msg("Waiting for connection...")
        await agent.detect_connection()

        async for option in prompt_loop(
            "(1) Issue Credential, (2) Send Proof Request, "
            + "(3) Send Message (X) Exit? [1/2/3/X] "
        ):
            if option is None or option in "xX":
                break

            elif option == "1":
                log_status("#13 Issue credential offer to X")
                # TODO credential offer
                agent.cred_attrs[credential_definition_id] = {
                    "employee_id": "ACME0009",
                    "name": "Alice Smith",
                    "date": "2019-06-30",
                    "position": "CEO",
                }

                cred_preview = {
                    "@type": CRED_PREVIEW_TYPE,
                    "attributes": [
                        {"name": n, "value": v}
                        for (n, v) in agent.cred_attrs[credential_definition_id].items()
                    ],
                }

                offer_request = {
                    "credential_definition_id": credential_definition_id,
                    "connection_id": agent.connection_id,
                    "comment": f"Offer on cred def id {credential_definition_id}",
                    "credential_preview": cred_preview,
                }
                await agent.admin_POST("/credential_exchange/send-offer", offer_request)
'''
                log_status("#13 Issue credential offer 2 to X")
                # TODO credential offers
                offer_2 = {
                    "credential_definition_id": credential_definition_id_2,
                    "connection_id": agent.connection_id,
                }
                agent.cred_attrs[credential_definition_id_2] = {
                    "employee_id": "ACME0009",
                    "name": "Alice Smith",
                    "date": "2019-06-30",
                    "salary": "120000",
                }
                await agent.admin_POST("/credential_exchange/send-offer", offer_2)
'''
            elif option == "2":
                log_status("#20 Request proof of degree from alice")
                # TODO presentation requests
                proof_attrs = [
                    {"name": "name", "restrictions": [{"schema_name": "degree schema"}]},
                    #{"name": "student_id", "restrictions": [{"schema_name": "degree schema", "attr::name::value": "Alice Smith"}]},
                    {"name": "date", "restrictions": [{"schema_name": "degree schema"}]}, #, "attr::name::value": "Alice Smith"}]},
                    {"name": "degree", "restrictions": [{"schema_name": "degree schema"}]}, #, "attr::name::value": "Alice Smith"}]},
                ]
                proof_predicates = []
                proof_request = {
                    "name": "Proof of Education",
                    "version": "1.0",
                    "connection_id": agent.connection_id,
                    "requested_attributes": proof_attrs,
                    "requested_predicates": proof_predicates,
                }
                agent.log("Proof request:", json.dumps(proof_request))
                await agent.admin_POST(
                    "/presentation_exchange/send_request", proof_request
                )

            elif option == "3":
                msg = await prompt("Enter message: ")
                await agent.admin_POST(
                    f"/connections/{agent.connection_id}/send-message", {"content": msg}
                )

        if show_timing:
            timing = await agent.fetch_timing()
            if timing:
                for line in agent.format_timing(timing):
                    log_msg(line)

    finally:
        terminated = True
        try:
            if agent:
                await agent.terminate()
        except Exception:
            LOGGER.exception("Error terminating agent:")
            terminated = False

    await asyncio.sleep(0.1)

    if not terminated:
        os._exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Runs a Faber demo agent.")
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8040,
        metavar=("<port>"),
        help="Choose the starting port number to listen on",
    )
    parser.add_argument(
        "--timing", action="store_true", help="Enable timing information"
    )
    args = parser.parse_args()

    require_indy()

    try:
        asyncio.get_event_loop().run_until_complete(main(args.port, args.timing))
    except KeyboardInterrupt:
        os._exit(1)
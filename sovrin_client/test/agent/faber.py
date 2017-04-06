from stp_core.common.log import getlogger
from sovrin_client.agent.runnable_agent import RunnableAgent
from sovrin_client.agent.agent import create_client
from sovrin_client.client.client import Client
from sovrin_client.test.agent.helper import bootstrap_schema
from sovrin_client.test.agent.mock_backend_system import MockBackendSystem

from anoncreds.protocol.types import AttribType, AttribDef
from sovrin_client.agent.agent import WalletedAgent
from sovrin_client.test.helper import primes
from sovrin_client.test.agent.helper import buildFaberWallet
from sovrin_client.test.helper import TestClient

logger = getlogger()


def create_faber(name=None, wallet=None, base_dir_path=None, port=5555, client=None):

    if client is None:
        client = create_client(base_dir_path=None, client_class=TestClient)

    endpoint_args = {'onlyListener': True}
    if wallet:
        endpoint_args['seed'] = wallet._signerById(wallet.defaultId).seed

    agent = WalletedAgent(name=name or "Faber College",
                          basedirpath=base_dir_path,
                          client=client,
                          wallet=wallet or buildFaberWallet(),
                          port=port,
                          endpointArgs=endpoint_args)

    agent._invites = {
        "b1134a647eb818069c089e7694f63e6d": 1,
        "2a2eb72eca8b404e8d412c5bf79f2640": 2,
        "7513d1397e87cada4214e2a650f603eb": 3,
        "710b78be79f29fc81335abaa4ee1c5e8": 4
    }

    transcript_def = AttribDef('Transcript',
                              [AttribType('student_name', encode=True),
                               AttribType('ssn', encode=True),
                               AttribType('degree', encode=True),
                               AttribType('year', encode=True),
                               AttribType('status', encode=True)])

    agent.add_attribute_definition(transcript_def)

    backend = MockBackendSystem(transcript_def)

    backend.add_record(1,
                       student_name="Alice Garcia",
                       ssn="123-45-6789",
                       degree="Bachelor of Science, Marketing",
                       year="2015",
                       status="graduated")

    backend.add_record(2,
                       student_name="Carol Atkinson",
                       ssn="783-41-2695",
                       degree="Bachelor of Science, Physics",
                       year="2012",
                       status="graduated")

    backend.add_record(3,
                       student_name="Frank Jeffrey",
                       ssn="996-54-1211",
                       degree="Bachelor of Arts, History",
                       year="2013",
                       status="dropped")

    backend.add_record(4,
                       student_name="Bob Richards",
                       ssn="151-44-5876",
                       degree="MBA, Finance",
                       year="2015",
                       status="graduated")

    agent.set_issuer_backend(backend)

    return agent

async def bootstrap_faber(agent):
    schema_id = await bootstrap_schema(agent,
                                 'Transcript',
                                 'Transcript',
                                 '1.2',
                                 primes["prime1"][0],
                                 primes["prime1"][1])

    await agent._set_available_claim_by_internal_id(1, schema_id)
    await agent._set_available_claim_by_internal_id(2, schema_id)
    await agent._set_available_claim_by_internal_id(3, schema_id)
    await agent._set_available_claim_by_internal_id(4, schema_id)


if __name__ == "__main__":
    args = RunnableAgent.parser_cmd_args()
    port = args[0]
    if port is None:
        port = 5555
    agent = create_faber(name="Faber College", wallet=buildFaberWallet(), base_dir_path=None, port=port)
    RunnableAgent.run_agent(agent, bootstrap=bootstrap_faber(agent))


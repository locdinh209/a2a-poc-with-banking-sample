import logging
from typing import Dict, Any
import httpx
from a2a.client import A2AClient
from a2a.types import AgentCard, MessageSendParams, SendMessageRequest, SendStreamingMessageRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BankingOrchestrator:
    """Orchestrates multi-agent banking workflows via A2A."""
    
    def __init__(self, logger_util=None):
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.logger_util = logger_util
        self.http_cli = httpx.AsyncClient(timeout=httpx.Timeout(120.0))
        
    async def close(self):
        await self.http_cli.aclose()
    
    async def discover_agents(self, urls: list[str]):
        """Discover agent capabilities from Agent Cards."""
        from a2a.client.card_resolver import A2ACardResolver
        
        for url in urls:
            resolver = A2ACardResolver(httpx_client=self.http_cli, base_url=url)
            try:
                card = await resolver.get_agent_card()
                # A2AClient is deprecated, use ClientFactory in real implementation
                client = A2AClient(httpx_client=self.http_cli, agent_card=card)
                
                self.agents[card.name] = {
                    "url": url,
                    "card": card,
                    "client": client
                }
                if self.logger_util:
                    self.logger_util.log_discovery(url, card.model_dump())
                else:
                    logger.info(f"Discovered {card.name} at {url}")
            except Exception as e:
                logger.error(f"Failed to discover agent at {url}: {e}")

    async def get_agent_response(self, agent_name: str, message: str) -> str:
        """Send a message to an agent and wait for the completion artifact."""
        if agent_name not in self.agents:
            raise ValueError(f"Agent {agent_name} not discovered.")
            
        client = self.agents[agent_name]["client"]
        
        from uuid import uuid4
        
        request = SendMessageRequest(
            id=str(uuid4()), 
            params=MessageSendParams(
                message={
                    'role': 'user',
                    'parts': [{'kind': 'text', 'text': message}],
                    'message_id': uuid4().hex,
                }
            )
        )
        
        if self.logger_util:
            self.logger_util.log_send_message(agent_name, message, request.id)
        else:
            logger.info(f"Sending message to {agent_name}: {message}")
            
        response = await client.send_message(request)
        
        result = response.root.result
        
        if self.logger_util:
            self.logger_util.log_task_status(agent_name, result.id, result.status.state)
        
        if result.status.state == 'completed':
            # Return the artifact text
            if result.artifacts and len(result.artifacts) > 0:
                artifact_part = result.artifacts[0].parts[0]
                if hasattr(artifact_part, 'model_dump'):
                    data = artifact_part.model_dump()
                    if isinstance(data, dict):
                        if 'text' in data:
                            artifact_text = data['text']
                        elif 'root' in data and isinstance(data['root'], dict) and 'text' in data['root']:
                            artifact_text = data['root']['text']
                        else:
                            artifact_text = str(data)
                    else:
                        artifact_text = str(data)
                elif hasattr(artifact_part, 'text'):
                    artifact_text = artifact_part.text
                elif hasattr(artifact_part, 'root') and hasattr(artifact_part.root, 'text'):
                    artifact_text = artifact_part.root.text
                else:
                    artifact_text = str(artifact_part)
                
                if self.logger_util:
                    self.logger_util.log_artifact(agent_name, result.artifacts[0].name, artifact_text)
                return artifact_text
            return "Completed with no artifact"
        elif result.status.state == 'input-required':
            msg_part = result.status.message.parts[0]
            if hasattr(msg_part, 'model_dump'):
                data = msg_part.model_dump()
                txt = data.get('text', str(data))
                if isinstance(data, dict) and 'root' in data and isinstance(data['root'], dict):
                    txt = data['root'].get('text', txt)
            else:
                txt = getattr(msg_part, 'text', str(msg_part))
            return f"Input Required: {txt}"
        else:
            return f"Failed with state: {result.status.state}"
    async def process_loan_application(self, customer_id: str, name: str, dob: str, amount: float):
        """Full loan processing workflow using multiple agents."""
        steps = []
        import time
        
        logger.info(f"Starting loan processing for {customer_id}")
        
        # Step 1: KYC verification
        start_time = time.time()
        kyc_result = await self.get_agent_response(
            "Banking KYC Verification Agent",
            f"Verify KYC for customer {customer_id}, name {name}, dob {dob}."
        )
        duration = time.time() - start_time
        steps.append({"step": 1, "agent": "KYC Agent", "status": "✅" if "FAILED" not in kyc_result.upper() else "❌", "duration": f"{duration:.1f}s"})
        
        if "FAILED" in kyc_result.upper():
            return "Application Rejected: Failed KYC verification.", steps

        # Step 2: Transaction analysis
        start_time = time.time()
        txn_result = await self.get_agent_response(
            "Banking Transaction Analyzer Agent", 
            f"Analyze transactions and spending patterns for customer {customer_id}"
        )
        duration = time.time() - start_time
        steps.append({"step": 2, "agent": "Transaction Agent", "status": "✅", "duration": f"{duration:.1f}s"})

        # Step 3: Loan assessment
        start_time = time.time()
        loan_result = await self.get_agent_response(
            "Banking Loan Assessment Agent",
            f"Assess loan application for customer={customer_id}. Requested loan amount is ${amount}. "\
            f"Note their KYC is verified. Their spending pattern is: {txn_result}"
        )
        duration = time.time() - start_time
        steps.append({"step": 3, "agent": "Loan Agent", "status": "✅", "duration": f"{duration:.1f}s"})

        if self.logger_util:
            self.logger_util.log_workflow_summary(steps)
            
        return loan_result, steps

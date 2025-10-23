"""
LangChain Agent for Financial Document Analysis
Implements multi-tool agent for authenticity verification and financial analysis.
"""

from typing import Dict, Any, List, Optional
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage
import base64
import json
from document_utils import DocumentProcessor


class FinancialDocumentAnalyst:
    """
    Multi-tool LangChain agent for analyzing financial documents.
    Focuses on authenticity verification and generating follow-up questions.
    """

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        """
        Initialize the analyst agent.

        Args:
            api_key: OpenAI API key
            model: Model to use (gpt-4o has vision capabilities)
        """
        self.api_key = api_key
        self.model = model
        self.llm = ChatOpenAI(
            api_key=api_key,
            model=model,
            temperature=0.1  # Low temperature for consistent analysis
        )
        self.vision_llm = ChatOpenAI(
            api_key=api_key,
            model="gpt-4o",  # Vision model
            temperature=0.1
        )
        self.document_processor = DocumentProcessor()
        self.agent_executor = None
        self._setup_agent()

    def _setup_agent(self):
        """Set up the LangChain agent with tools."""
        tools = [
            Tool(
                name="analyze_metadata",
                func=self._analyze_metadata_tool,
                description="Analyzes document metadata to detect signs of tampering, editing, or fraudulent creation. Returns red flags and positive signals about document authenticity."
            ),
            Tool(
                name="visual_inspection",
                func=self._visual_inspection_tool,
                description="Performs detailed visual inspection of the document using vision AI to detect inconsistencies, alterations, suspicious patterns, or visual fraud indicators."
            ),
            Tool(
                name="financial_analysis",
                func=self._financial_analysis_tool,
                description="Analyzes financial data patterns in the document to assess income stability, cashflow consistency, and detect suspicious financial patterns."
            ),
        ]

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert financial document fraud analyst. Your job is to rigorously analyze uploaded documents to determine authenticity and assess financial credibility.

Your analysis should be:
1. THOROUGH - Use all available tools to gather evidence
2. OBJECTIVE - Present both positive and negative findings
3. DETAILED - Explain your reasoning for each finding
4. ACTIONABLE - Provide clear follow-up questions when confidence is low

Document Types You'll Analyze:
- Bank statements
- Tax returns (W-2, 1099, etc.)
- Pay stubs
- Investment account statements
- Proof of assets

Your Response Structure:
1. First, use analyze_metadata to check document properties
2. Then, use visual_inspection to examine the document visually
3. Finally, use financial_analysis to assess the financial data
4. Synthesize findings into an authenticity assessment

Red Flags to Watch For:
- Inconsistent fonts or formatting
- Suspicious editing software in metadata
- Round numbers or unrealistic patterns
- Missing standard banking elements (logos, account numbers, etc.)
- Poor quality or screenshots instead of originals
- Inconsistent dates or impossible transactions

Always provide:
- Overall authenticity score (0-100)
- List of specific concerns
- Follow-up questions to increase confidence
- Recommendation (approve/review/request_more/deny)"""),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_tools_agent(self.llm, tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True
        )

    def _analyze_metadata_tool(self, input_str: str) -> str:
        """Tool for metadata analysis."""
        # Input should be a JSON string with file_data and filename
        try:
            data = json.loads(input_str)
            file_data = base64.b64decode(data['file_data'])
            filename = data['filename']

            signals = self.document_processor.analyze_document_authenticity_signals(
                file_data, filename
            )

            result = {
                'red_flags': signals['red_flags'],
                'positive_signals': signals['positive_signals'],
                'metadata': signals['metadata_analysis']
            }

            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error analyzing metadata: {str(e)}"

    def _visual_inspection_tool(self, input_str: str) -> str:
        """Tool for visual document inspection using GPT-4 Vision."""
        try:
            data = json.loads(input_str)
            file_data = base64.b64decode(data['file_data'])
            filename = data['filename']
            document_type = data.get('document_type', 'financial document')

            # Encode image for vision model
            base64_image = base64.b64encode(file_data).decode('utf-8')

            # Determine image type
            file_ext = filename.lower().split('.')[-1]
            if file_ext == 'pdf':
                # For PDFs, we'd need to convert to image first
                # For now, return a message that we need image format
                return json.dumps({
                    "note": "PDF visual inspection requires conversion to image. For best results, upload as PNG/JPG.",
                    "visual_analysis": "Unable to perform visual inspection on PDF directly."
                })

            # Create vision analysis prompt
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""Analyze this {document_type} image for signs of authenticity or fraud.

Look for:
1. **Visual Consistency**: Are fonts, sizes, and spacing consistent throughout?
2. **Professional Quality**: Does it look professionally generated or hand-edited?
3. **Standard Elements**: Are typical banking/financial elements present (logos, routing numbers, formatting)?
4. **Editing Artifacts**: Signs of copy-paste, white-out, or digital manipulation
5. **Screenshot Indicators**: Is this a screenshot vs. original document?
6. **Text Quality**: OCR artifacts, pixelation, or unusual rendering
7. **Suspicious Patterns**: Whited-out sections, alignment issues, color inconsistencies

Provide a detailed visual analysis with specific observations."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]

            response = self.vision_llm.invoke(messages)
            return response.content

        except Exception as e:
            return f"Error during visual inspection: {str(e)}"

    def _financial_analysis_tool(self, input_str: str) -> str:
        """Tool for analyzing financial data patterns."""
        try:
            data = json.loads(input_str)
            # In a real implementation, this would extract and analyze numerical data
            # For now, we'll rely on the vision model to read numbers

            prompt = """Based on the financial data visible in the document, analyze:

1. **Income Consistency**: Are income deposits regular and consistent?
2. **Expense Patterns**: Do expenses look realistic for stated income?
3. **Red Flag Transactions**: Unusual large deposits/withdrawals, round numbers
4. **Balance Trends**: Does balance behave realistically over time?
5. **NSF/Overdrafts**: Any bounced payments or overdraft indicators?
6. **Transaction Authenticity**: Do transaction descriptions look legitimate?

Provide specific observations about financial patterns."""

            return prompt + "\n\nNote: Detailed numerical analysis requires OCR extraction. This is a visual assessment."

        except Exception as e:
            return f"Error during financial analysis: {str(e)}"

    def analyze_document(
        self,
        file_data: bytes,
        filename: str,
        document_type: str = "bank statement"
    ) -> Dict[str, Any]:
        """
        Main method to analyze a financial document.

        Args:
            file_data: Raw bytes of the uploaded file
            filename: Original filename
            document_type: Type of document (bank statement, tax return, etc.)

        Returns:
            Dictionary with analysis results
        """
        # Validate file first
        is_valid, error_msg = self.document_processor.validate_file(file_data, filename)
        if not is_valid:
            return {
                'success': False,
                'error': error_msg
            }

        # Prepare data for agent
        file_data_b64 = base64.b64encode(file_data).decode('utf-8')
        tool_input = json.dumps({
            'file_data': file_data_b64,
            'filename': filename,
            'document_type': document_type
        })

        # Create analysis request
        analysis_request = f"""Analyze the following {document_type} for authenticity and financial credibility:

Filename: {filename}
Size: {len(file_data) / 1024:.2f} KB

Please perform a complete analysis using all available tools and provide:
1. Authenticity score (0-100)
2. List of red flags found
3. List of positive signals
4. 3-5 specific follow-up questions for the customer
5. Recommended action (approve/review/request_more/deny)

Tool Input Data: {tool_input}"""

        try:
            # Run the agent
            result = self.agent_executor.invoke({
                "input": analysis_request
            })

            return {
                'success': True,
                'analysis': result.get('output', ''),
                'raw_result': result
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Analysis failed: {str(e)}"
            }

    def generate_follow_up_questions(self, analysis_result: str) -> List[str]:
        """
        Generate targeted follow-up questions based on analysis results.
        """
        prompt = f"""Based on the following document analysis, generate 3-5 specific, targeted follow-up questions that would help increase confidence in the document's authenticity or clarify concerning findings.

Analysis:
{analysis_result}

Generate questions that:
1. Address specific red flags or concerns
2. Request additional documentation for verification
3. Ask for clarification on suspicious patterns
4. Are polite but direct
5. Help the customer understand what would strengthen their application

Return ONLY a JSON array of questions, no other text:
["question 1", "question 2", ...]"""

        try:
            response = self.llm.invoke(prompt)
            questions = json.loads(response.content)
            return questions
        except:
            return [
                "Can you provide the original PDF statement directly from your bank's online portal?",
                "Do you have additional months of statements to show consistency?",
                "Can you provide a verification contact at your financial institution?"
            ]


def create_analyst_agent(api_key: str) -> FinancialDocumentAnalyst:
    """Factory function to create analyst agent."""
    return FinancialDocumentAnalyst(api_key=api_key)

from pydantic import BaseModel, Field

# Response model for the calculator tools from the calculator-agent MCP server
class SupportResponse(BaseModel):
    stage: str = Field(description="Stage like answered, refunded or rejected")
    successful: bool
    message: str

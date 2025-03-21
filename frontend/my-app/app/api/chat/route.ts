import { NextResponse } from 'next/server';
import createClient from "@azure-rest/ai-inference";
import { AzureKeyCredential } from "@azure/core-auth";

const endpoint = "https://hackathonopenai997940562190.openai.azure.com/openai/deployments/gpt-4o";
const modelName = "gpt-4o";

if (!process.env.AZURE_LLM_KEY) {
  throw new Error("AZURE_LLM_KEY environment variable is not set");
}

const azureClient = createClient(
  endpoint,
  new AzureKeyCredential(process.env.AZURE_LLM_KEY)
);

export async function POST(request: Request) {
  try {
    const { messages, formData } = await request.json();
    
    // Create system prompt with form data
    const systemPrompt = `You are an AI agent designed specifically to give advice on a particular change management scenario.
This is your function and you must adhere to it.
Here are the details of the change management initiative:
Change Initiative Name: ${formData.change_initiative_name}
What industry does your business operate in? : ${formData.industry}
What services do you provide? : ${formData.services_provided}
Start Date : ${formData.start_date}
Department : ${formData.department.join(', ')}
What is the realistic budget range for this initiative (min)? : ${formData.min_budget}
What is the realistic budget range for this initiative (max)? : ${formData.max_budget}
Expected Completion Date : ${formData.end_date}
What business goals will this initiative address? : ${formData.targeted_business_goals}
Percentage of employees needing retraining? : ${formData.employee_retraining_percent}%
Number of affected employees: ${formData.num_affected_employees}
Employee morale (1-10): ${formData.employee_morale}
Change details: ${formData.change_details}
Based on this data, the user is expected to ask a few questions. Answer them to the best of your ability.
You can use markdown formatting to make your responses more readable. Use:
- Headers (##) for section titles
- Bullet points (-) for lists
- Bold text (**) for emphasis
- Code blocks (\`\`) for technical terms
- Numbered lists (1., 2., etc.) for steps or sequences
Keep your responses clear and well-structured.`;
    
    const response = await azureClient.path("/chat/completions").post({
      body: {
        messages: [
          {
            role: "system",
            content: systemPrompt
          },
          ...messages
        ],
        max_tokens: 4096,
        temperature: 0.7,
        top_p: 1,
        model: modelName,
        stream: false
      }
    });

    if (response.status !== "200") {
      throw new Error(`Failed to get chat completions, http operation failed with ${response.status} code`);
    }

    const result = response.body;
    if ('choices' in result) {
      return NextResponse.json({ content: result.choices[0].message.content || "I apologize, but I couldn't generate a response." });
    }
    throw new Error("Invalid response format");
  } catch (error) {
    console.error("Error getting chat completion:", error);
    return NextResponse.json(
      { error: "Failed to process request", details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    );
  }
}
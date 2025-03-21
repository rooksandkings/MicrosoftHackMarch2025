import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  const apiKey = process.env.AZURE_API_KEY;
  
  if (!apiKey) {
    console.error("AZURE_API_KEY is not defined in environment variables");
    return NextResponse.json(
      { error: "API key is not configured" }, 
      { status: 500 }
    );
  }

  try {
    // Get form data from the request
    const formData = await request.json();
    console.log("Received form data:", formData);
    
    // Set up request to Azure
    const requestHeaders = new Headers({"Content-Type": "application/json"});
    requestHeaders.append("Authorization", "Bearer " + apiKey);
    requestHeaders.append("azureml-model-deployment", "hackathon2025-beta-dgese-1");
    
    const url = "https://hackathon2025-beta-dgese.eastus2.inference.ml.azure.com/score";
    console.log("Making request to Azure ML endpoint:", url);
    
    // Forward the request to Azure
    const azureResponse = await fetch(url, {
      method: "POST",
      body: JSON.stringify(formData),
      headers: requestHeaders
    });
    
    if (!azureResponse.ok) {
      const errorText = await azureResponse.text();
      console.error("Azure API error response:", {
        status: azureResponse.status,
        statusText: azureResponse.statusText,
        body: errorText
      });
      return NextResponse.json(
        { error: `Azure API error: ${azureResponse.status} - ${errorText}` }, 
        { status: azureResponse.status }
      );
    }
    
    // Return the Azure response
    const result = await azureResponse.json();
    console.log("Azure API successful response:", result);
    return NextResponse.json(result);
  } catch (error) {
    console.error("Error in ROI calculation API:", error);
    return NextResponse.json(
      { error: "Failed to process request", details: error instanceof Error ? error.message : String(error) }, 
      { status: 500 }
    );
  }
} 
import * as vscode from "vscode";
import { Configuration, OpenAIApi } from "openai";

let openai: OpenAIApi | undefined = undefined;

const openAiRequest = async (text: string) => {
  // Create a new OpenAI instance if it doesn't exist
  if (openai === undefined) {
    const openaiApiKey: string =
      vscode.workspace.getConfiguration("assistant").get("openaikey") || "";
    const configuration = new Configuration({
      apiKey: openaiApiKey,
    });
    openai = new OpenAIApi(configuration);
  }

  console.time("openAiRequest");
  console.log("Sending OpenAI request...");
  const response = await openai.createChatCompletion({
    model: "gpt-3.5-turbo",
    messages: [
      {
        role: "user",
        content: text,
      },
    ],
  });
  console.log("OpenAI response", response);
  console.timeEnd("openAiRequest");
  return response;
};

export function activate(context: vscode.ExtensionContext) {
  // register a content provider for the assistant-scheme
  let globalAssistantBuffer: string = "";
  const assistantUriScheme = "asssitant";
  const uri = vscode.Uri.parse(`${assistantUriScheme}:Assistant`);

  const myProvider = new (class implements vscode.TextDocumentContentProvider {
    onDidChangeEmitter = new vscode.EventEmitter<vscode.Uri>();
    onDidChange = this.onDidChangeEmitter.event;
    provideTextDocumentContent(): string {
      return globalAssistantBuffer;
    }
  })();

  context.subscriptions.push(
    vscode.workspace.registerTextDocumentContentProvider(
      assistantUriScheme,
      myProvider
    )
  );

  // register a command for the assistant
  let disposable = vscode.commands.registerCommand(
    "assistant.run",
    async function () {
      const updateText = function (text: string) {
        globalAssistantBuffer = text;
        myProvider.onDidChangeEmitter.fire(uri);
      };
      try {
        let highlightedText = "";
        const editor = vscode.window.activeTextEditor;
        if (editor === undefined) {
          vscode.window.showInformationMessage("No active Text Editor");
          return;
        }
        if (editor.selection && !editor.selection.isEmpty) {
          // Use the highlighted text
          const selectionRange = new vscode.Range(
            editor.selection.start.line,
            editor.selection.start.character,
            editor.selection.end.line,
            editor.selection.end.character
          );
          highlightedText = editor.document.getText(selectionRange);
        } else {
          // Use the active file's text
          highlightedText = editor.document.getText();
        }

        // Ask for what the User wants to do
        const userRequest = await vscode.window.showInputBox({
          placeHolder: "Help me with...",
          prompt: "Ask Assistant to help me with",
        });
        if (userRequest === "" || userRequest === undefined) {
          vscode.window.showErrorMessage(
            "You have to ask the assistant for help with something"
          );
        }

        // Open a new document with the assistant-scheme
        const doc = await vscode.workspace.openTextDocument(uri);

        const newTextEditor = await vscode.window.showTextDocument(doc, {
          viewColumn: vscode.ViewColumn.Beside,
          preserveFocus: true,
          preview: false,
        });

        // Send the highlighted text to OpenAI and update the assistant document
        const request = userRequest + '\n"""\n' + highlightedText + '\n"""\n';
        updateText("Asking Assistant...\n" + request);
        const response = await openAiRequest(request);
        updateText(
          response.data?.choices[0]?.message?.content ||
            JSON.stringify(response)
        );
      } catch (error) {
        let message = "Unknown Error: " + error;
        if (error instanceof Error && error.message) {
          message = error.message;
        }
        updateText(message);
        vscode.window.showErrorMessage(message);
      }
    }
  );
  context.subscriptions.push(disposable);
}
export function deactivate() {}

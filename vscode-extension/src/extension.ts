import * as vscode from "vscode";
import { Configuration, OpenAIApi } from "openai";

const configuration = new Configuration({
  apiKey: "",
});
const openai = new OpenAIApi(configuration);

const openAiRequest = async (text: string) => {
  // This function sends a request to OpenAI and returns the response
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
        // Get the currently highlighted text
        const editor = vscode.window.activeTextEditor;
        if (editor === undefined) {
          vscode.window.showInformationMessage("No active Text Editor");
          return;
        }
        const document = editor.document;
        const highlightedText = document.getText(
          document.getWordRangeAtPosition(editor.selection.active)
        );

        // Open a new document with the assistant-scheme
        const doc = await vscode.workspace.openTextDocument(uri);

        const newTextEditor = await vscode.window.showTextDocument(doc, {
          viewColumn: vscode.ViewColumn.Beside,
          preserveFocus: true,
          preview: false,
        });

        // Send the highlighted text to OpenAI and update the assistant document
        updateText('Asking Assistant...\n\n"""\n' + highlightedText + '\n"""');
        const response = await openAiRequest(highlightedText);
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

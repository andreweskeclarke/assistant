define(['base/js/namespace', 'jquery'], function(Jupyter, $) {
  function uuidv4() {
    return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
      (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    );
  }

  function buildAssistant() {
    // Send messages to local server, which forwards them to the Assistant's RabbitMQ instance
    var ws = new WebSocket('ws://localhost:8980/ws');
    ws.onmessage = function (event) {
      const response = JSON.parse(event.data);
      const cell = Jupyter.notebook.insert_cell_below();
      cell.set_text(response['text']);
    };

    return function() {
      // Get the current cell contents and send them to the Assistant
      var code = "";
      for (let i = 0; i <= Jupyter.notebook.get_selected_index(); i++) {
        const cell = Jupyter.notebook.get_cell(i);
        var cellAsText = `\`\`\`python\n${cell.get_text()}\`\`\`\n`;
        const outputs = cell.output_area.outputs;
        for (const output of outputs) {
          var outputContents = "";
          if (output["output_type"] == "execute_result") {
            outputContents = output["data"]["text/plain"];
          }  else if (output["output_type"] == "stream") {
            outputContents = output["text"];
          } else if (output["output_type"] == "error") {
            outputContents = `Error! ${output["ename"]}: ${output["evalue"]}`;
          } else { 
            outputContents = JSON.stringify(output.toJSON());
          }
          cellAsText += outputContents.slice(0, 750)
        }
        code += cellAsText;
      }
      ws.send(code);
    }
  }

  function load_ipython_extension() {
    const assistant = buildAssistant();
    const assistantAction = Jupyter.actions.register({
      'help': 'AI Assistant - Suggest code',
      'help_index': 'zz',
      'icon': 'fa-magic',
      'handler': assistant
    }, 'send', 'assistant');

    Jupyter.toolbar.add_buttons_group([assistantAction]);
    Jupyter.keyboard_manager.command_shortcuts.add_shortcut('ctrl-shift-enter', assistantAction);
    Jupyter.keyboard_manager.edit_shortcuts.add_shortcut('ctrl-shift-enter', assistantAction);
  }

  return {
    load_ipython_extension: load_ipython_extension
  };
});


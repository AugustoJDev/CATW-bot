const { SlashCommandBuilder } = require('discord.js');
const path = require('node:path');
const { spawn } = require('node:child_process');

// Commands don't need to have their names written here, just set the filename
module.exports = {
	data: new SlashCommandBuilder()
		.setName(basename(__filename))
		.setDescription('Base for commands.')
        .addStringOption(option => 
            option.setName('url')
                .setDescription('URL do post/storie/reel')
                .setRequired(true)
        ),
	async execute(interaction) {

        const scriptPath = path.resolve(__dirname, "../../../python/webhooks/instagram.py");
        const url = interaction.options.getString('url');

        interaction.reply({
			content: `Chamando webhook para a URL: \`${url}\``,
            ephemeral: true
		})

        const pythonProcess = spawn("py", [scriptPath, url]);

        let responseData = "";

        // Captura a saída do script Python
        pythonProcess.stdout.on("data", (data) => {
            responseData += data.toString();
        });

        // Captura erros do script Python
        pythonProcess.stderr.on("data", (data) => {
            console.error(`Erro no script Python: ${data.toString()}`);
        });

        // Quando o script Python finaliza, processamos os dados
        pythonProcess.on("close", (code) => {
            if (code !== 0) {
                console.error(`Processo Python finalizado com código de erro: ${code}`);
                return;
            }

            try {
                const dados = JSON.parse(responseData.trim());
                console.log("📌 Dados do Instagram:", dados);
            } catch (parseError) {
                console.error("❌ Erro ao interpretar resposta JSON:", parseError);
            }
        });
	},
};
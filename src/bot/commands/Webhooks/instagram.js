const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');
const path = require('node:path');
const { spawn } = require('node:child_process');
const { basename } = require('node:path');
const getEmoji = require('../../config/getEmojis');

// Commands don't need to have their names written here, just set the filename
module.exports = {
    data: new SlashCommandBuilder()
        .setName(basename(__filename).replace('.js', ''))
        .setDescription('Send Instagram post to a specified channel.')
        .addStringOption(option => 
            option.setName('url')
                .setDescription('Post/Storie/Reel URL')
                .setRequired(true)
        ),
    async execute(interaction) {
        const scriptPath = path.resolve(__dirname, "../../../python/webhooks/instagram.py");
        const url = interaction.options.getString('url');
        const loadingEmoji = await getEmoji("loading");

        await interaction.reply({
            content: `${loadingEmoji} Getting URL informations... URL: \`${url}\``,
            ephemeral: true
        });

        console.log(`Executing script: ${scriptPath} with URL: ${url}`);

        const pythonProcess = spawn("python", [scriptPath, url]);

        let responseData = "";
        let errorData = "";

        // Capture the output from the Python script
        pythonProcess.stdout.on("data", (data) => {
            console.log(`stdout: ${data}`);
            responseData += data.toString();
        });

        // Capture errors from the Python script
        pythonProcess.stderr.on("data", (data) => {
            console.error(`stderr: ${data}`);
            errorData += data.toString();
        });

        // When the Python script finishes, process the data
        pythonProcess.on("close", async (code) => {
            console.log(`Python script finished with code: ${code}`);
            if (code !== 0) {
                console.error(`Process ended with the error code: ${code}`);
                await interaction.editReply({
                    content: `❌ Error: Process ended with the error code: ${code}`
                });
                return;
            }

            if (errorData) {
                console.error(`Python script error output: ${errorData}`);
            }

            try {
                console.log(`Response data: ${responseData.trim()}`);
                const dados = JSON.parse(responseData.trim());
                
                if (dados.error) {
                    await interaction.editReply({
                        content: `❌ Error: ${dados.error}`
                    });
                    return;
                }

                let instagramEmbed = new EmbedBuilder()
                    .setTitle(`Instagram ${dados.type}`)
                    .setURL(url)
                    .setDescription(dados.description || "No Description")
                    .setImage(dados.thumbnail || "")
                    .setColor("#C13584")
                    .setFooter({ text: `Author: ${dados.author}` })
                    .setTimestamp(new Date(dados.taken_at));

                if (dados.video_url) {
                    instagramEmbed.addFields({ name: "Video URL", value: dados.video_url });
                }

                await interaction.editReply({
                    content: `✅ Successfully fetched and posted the Instagram URL: \`${url}\``,
                    embeds: [instagramEmbed]
                });
            } catch (parseError) {
                console.error("❌ Error interpreting JSON response:", parseError);
                await interaction.editReply({
                    content: `❌ Error interpreting JSON response: ${parseError.message}`
                });
            }
        });
    },
};
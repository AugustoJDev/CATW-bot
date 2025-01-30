const { SlashCommandBuilder, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');
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

        if(url.includes("stories") || url.includes("story")) {
            await interaction.reply({
                content: `❌ Error: Stories are not supported. Please use a post or reel URL.`,
                ephemeral: true
            });
            return;
        }

        await interaction.reply({
            content: `${loadingEmoji} Getting URL informations... URL: \`${url}\``,
            ephemeral: true
        });

        const pythonProcess = spawn("py", [scriptPath, url]);

        let responseData = "";
        let errorData = "";

        // Capture the output from the Python script
        pythonProcess.stdout.on("data", (data) => {
            responseData += data.toString();
        });

        // Capture errors from the Python script
        pythonProcess.stderr.on("data", (data) => {
            errorData += data.toString();
        });

        // When the Python script finishes, process the data
        pythonProcess.on("close", async (code) => {
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
                const dados = JSON.parse(responseData.trim());
                
                let instagramEmbed = new EmbedBuilder()
                    .setAuthor({ name: dados.author || "No Username", iconURL: dados.author_image || ""})
                    .setURL(url || "https://instagram.com")
                    .setDescription(`✨ **Não esqueça de deixar seu like e comentário na postagem para nos ajudar!**`)
                    .addFields([{
                        name: "📩 | Descrição do Post",
                        value: dados.description,
                        inline: false
                    }])
                    .setImage(dados.thumbnail || "")
                    .setColor("#C13584")
                    .setTimestamp();

                let instagramButton = new ButtonBuilder()
                    .setStyle(ButtonStyle.Link)
                    .setLabel("View Post")
                    .setURL(url)
                    .setEmoji("1334517577510293534");

                let instagramActionRow = new ActionRowBuilder()
                    .addComponents(instagramButton);

                let { instagram } = require('../../JSON/channels.json');
                
                const channel = await interaction.client.channels.fetch(instagram);
                await channel.send({ 
                    content: "@everyone",
                    embeds: [instagramEmbed],
                    components: [instagramActionRow]
                });

                await interaction.editReply({
                    content: `✅ Successfully fetched and posted the Instagram URL: \`${url}\``
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
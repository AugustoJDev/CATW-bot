async function getEmoji(emojiIdentifier) {
    // Fetch all emojis from the guild
    const emojis = await client.guilds.cache.first().emojis.fetch();

    // Check if the identifier is a number (ID) or a string (name)
    if (isNaN(emojiIdentifier)) {
        // Search by name
        const emoji = emojis.find(e => e.name === emojiIdentifier);
        if (emoji) {
            return emoji.toString();
        }
    } else {
        // Search by ID
        const emoji = emojis.get(emojiIdentifier);
        if (emoji) {
            return emoji.toString();
        }
    }

    // Return null if no emoji is found
    return null;
}

module.exports = getEmoji;
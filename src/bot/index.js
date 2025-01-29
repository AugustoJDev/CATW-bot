require("dotenv").config();

// Enable or disable console logs for this events
global.logs = {
    Errors: true,
    CommandsLoaded: true,
    EventsLoaded: true,
    Ready: true
}

module.exports = {
	Client: require("./config/client.js"),
    ErrorsCatch: require("./config/error.js"),
    Events: require("./events/interactionCreate.js")
};
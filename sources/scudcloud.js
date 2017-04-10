// Fixes MutationObserver in Qt 5.2.1 (#551)
var MutationObserver = MutationObserver || WebKitMutationObserver;
ScudCloud = {
	unloaded: true,
	// This will fix Preferences > Advanced Options (#469)
	env: { mac_ssb_version: 1 },
	// App functions
	hasPreference: function(name){
		return false;
	},
	getPreference: function(name){
		return false;
	},
	setPreference: function(name, value){
		return false;
	},
	canShowHtmlNotifications: function(){
		// Ubuntu cannot display HTML notifications
		return false;
	},
    // Uploading doesn't work in some cases when slack cannot call getModifierKeys on this variable.
    // This works, even if nothing is being returned
    app: {
        getModifierKeys: function() {
            //TODO: actually get modifier keys
        }
    },
	// TSSSB.call
	call: function(name, args){
		ScudCloud.log(name, args);
		switch(name){
			case "reload":
				return ScudCloud.reload();
			case "didStartLoading":
				return ScudCloud.didStartLoading();
			case "didFinishLoading":
				return ScudCloud.didFinishLoading();
			case "setConnectionStatus":
				return ScudCloud.setConnectionStatus(args);
			case "notify":
				return ScudCloud.notify(args);
			case "setBadgeCount":
				return ScudCloud.setBadgeCount(args);
			case "displayTeam":
				return ScudCloud.displayTeam(args);
			case "signInTeam":
				return ScudCloud.signInTeam();
		}
		return false;
	},
	// TSSSB.call implementations
	reload: function(){
		window.location.reload();
	},
	didStartLoading: function(){
	},
	didFinishLoading: function(){
		TS.ui.banner.close();
		ScudCloud.populate();
		ScudCloud.unloaded = false;
	},
	setConnectionStatus: function(status){
		// "online", "connecting", "offline"
		switch(status){
			case "online": desktop.enableMenus(true); break;
			default: desktop.enableMenus(false);
		}
	},
	notify: function(args){
		desktop.sendMessage(args.title, args.content);
	},
	setBadgeCount: function(args){
		desktop.count(args.all_unread_highlights_cnt, args.all_unread_cnt);
	},
	signInTeam: function(){
		desktop.addTeam();
	},
	displayTeam: function(id){
	},
	// ScudCloud internal functions
	log: function(name, args){
		// Sometimes stringify will fail with complex objects. Specifically, it'll break message edit (#)
		try {
			if("object"== typeof(args)) args = JSON.stringify(args);
		} catch (e) {
			args = '';
		}
		console.log("ScudCloud."+name+", args: "+args);
	},
	populate: function(){
		// Let's really check if image_44 is ready (Fixes #554)
		if('undefined'!= TS && TS.model && TS.model.team && TS.model.team.icon && TS.model.team.icon.image_44){
			desktop.populate(JSON.stringify({'channels': ScudCloud.listChannels(), 'teams': ScudCloud.listTeams(), 'icon': TS.model.team.icon.image_44}));
		} else {
			setTimeout(ScudCloud.populate, 500);
		}
	},
	createSnippet: function(){
		return TS.ui.snippet_dialog.start();
	},
	listChannels: function(){
		var channels = TS.channels.getUnarchivedChannelsForUser();
		channels.push(TS.channels.getChannelById(TS.model.active_channel_id));
		return channels;
	},
	listTeams: function(){
		var currentTeam = {
			id: TS.boot_data.user_id,
			team_color: null,
			team_icon: TS.model.team.icon,
			team_id: TS.model.team.id,
			team_name: TS.model.team.name,
			team_url: "https://" + TS.model.team.domain + ".slack.com/"
		};
		var teams = [currentTeam];
		for(var id in TS.boot_data.other_accounts){
			teams.push(TS.boot_data.other_accounts[id]);
		}
		return teams;
	},
	quicklist: function(){
		desktop.quicklist(ScudCloud.listChannels());
	},
	join: function(c){
		return TS.channels.join(c);
	},
	setClipboard: function(data){
		TS.client.ui.file_pasted_sig.dispatch(data, TS.model.shift_key_pressed);
	},
	sendTickle: function(){
		return TS.ms.sendTickle();
	},
	preferences: function(){
		return TS.ui.prefs_dialog.start();
	},
	addTeam: function(){
		document.location = TS.boot_data.signin_url;
	},
	getCurrentTeam: function(){
		if(TS.boot_data.user_id){
			return TS.boot_data.user_id;
		}
		return "";
	},
	logout: function(){
		document.location = TS.boot_data.logout_url;
	},
	help: function(){
		return TS.help_dialog.start();
	}
};
document.onpaste = function(e){desktop.pasted(false);};
// Forcing call button handling
$('body').delegate('#channel_calls_button', 'click', function(){desktop.open(TS.boot_data.team_url+'call/'+TS.model.active_cid);});
window.winssb = TSSSB = ScudCloud;
// Sometimes didFinishLoading is not loaded
if(ScudCloud.unloaded){
	ScudCloud.didFinishLoading();
}

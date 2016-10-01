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
		// Wait until image_44 get ready (Fixes #454)
		setTimeout(function(){
			desktop.populate(JSON.stringify({'channels': ScudCloud.listChannels(), 'teams': ScudCloud.listTeams(), 'icon': TS.model.team.icon.image_44}));
		}, 500);
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
		var list = TS.getAllTeams();
		// Fix for current team displaying no icon
		list[0].team_icon = {"image_44":TS.model.team.icon.image_44};
		return list;
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
		var list = TS.getAllTeams();
		if(list!=null) for(var i=0;list.length;i++){
			if(list[i].team_url==TS.boot_data.team_url){
				return list[i].id;
			}
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
// Forcing new posts to get opened in system browser (Fixes #225)
$('body').delegate('a[href="/files/create/space"]', 'click', function(){desktop.open(TS.boot_data.team_url+'files/create/space');});
// Fixing profile display CSS (Fixes #396)
$('body').delegate('#client-ui', 'DOMNodeInserted',
    function(){
        var obj = $('.member_preview_link.member_image.thumb_512');
        if(obj.length > 0){
            var style = obj.attr('style');
						if(-1==style.indexOf('-webkit-linear-gradient')){
							obj.attr('style', style.replace('linear-gradient', '-webkit-linear-gradient'));
						}
        }
    }
);
// Forcing call button handling
$('body').delegate('#channel_calls_button', 'click', function(){desktop.open(TS.boot_data.team_url+'call/'+TS.model.active_cid);});
window.winssb = TSSSB = ScudCloud;
// Sometimes didFinishLoading is not loaded
if(ScudCloud.unloaded){
	ScudCloud.didFinishLoading();
}

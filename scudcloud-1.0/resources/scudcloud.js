function Notification(title, options){ 
	this.permission = 'granted'; 
    desktop.sendMessage(title, options.body);
}
Notification.permission = 'granted'; 
Notification.requestPermission = function(callback){ 
	if(undefined != typeof callback) callback(); 
}
var ScudCloud = {
	init: function(){
		document.onpaste = function(e){desktop.pasted(false);}
		TS.ui.growls.getPermissionLevel = function() { return 'granted'}
		TS.ui.growls.show = function(j,k,g,o,l,b,c,m){
			new Notification(j,{body:g,icon:TS.boot_data.img.app_icon,tag:"tag_"+(c?c.id||c.ts||new Date().getTime():new Date().getTime())})
		}
		TS.ms.connected_sig.add(function(){desktop.enableMenus(true);});
		TS.ms.disconnected_sig.add(function(){desktop.enableMenus(false);});
		ScudCloud.watch();
	},
    count: function(){
		var total=0; 
		$('span.unread_highlight').not('.hidden').each(function(i){ 
			total+= new Number($(this).text().replace('+','')); }
		);
		desktop.count(total.toString());
    },
    listChannels: function(){
		return TS.channels.getUnarchivedChannelsForUser();
	},
    listTeams: function(){
		return TS.getAllTeams();
	},
    quicklist: function(){
		desktop.quicklist(ScudCloud.listChannels());
	},
    watch: function(){
		setInterval(function(){
			ScudCloud.count();
		}, 1000);
	},
	join: function(c){
		return TS.channels.join(c);
	},
	setClipboard: function(data){
		TS.client.ui.file_pasted_sig.dispatch(data, TS.model.shift_key_pressed);
	},
    preferences: function(){
		return TS.ui.prefs_dialog.start();
	},
    addTeam: function(){
		document.location = TS.boot_data.signin_url;
	},
    logout: function(){
		document.location = TS.boot_data.logout_url;
	},
    help: function(){
		return TS.help_dialog.start();
	},
    isConnected: function(){
        return "undefined" != typeof TS && "undefined" != typeof TS.model && TS.model.ms_connected;
    }
}
var boot_data = {};
if("undefined" != typeof TS){
	ScudCloud.init();
    boot_data.channels = ScudCloud.listChannels();
    boot_data.teams = ScudCloud.listTeams();
} else {
    boot_data.channels = new Array();
    boot_data.teams = new Array();
}
boot_data

var LeftPane = {
	addTeam: function(id, name, url, icon, active){
		var node = document.getElementById(id);
        if(node === null){
			var ul = document.getElementById('teams');
			var li = document.createElement('li');
			li.id = id;
			li.setAttribute("onclick", "LeftPane.switchTo('"+id.replace(/'/g, '&quot;')+"','"+url.replace(/'/g, '&quot;')+"')");
			li.setAttribute("title", name);
			li.innerHTML = name[0];
			if( icon ){
			  li.style.backgroundImage = "url('"+ icon.replace(/'/g, '&quot;') +"')";
			  li.innerHTML = "";
			}
			var div = document.createElement('div');
			div.id = id+"_highlight";
			div.setAttribute("class", "highlight hidden");
			div.innerHTML = "1";
			ul.appendChild(li);
			li.appendChild(div);
			if(active){
				LeftPane.setActive(id);
			}
			LeftPane.switchTo(id, url);
		}
	},
	click: function(i){
		var list = document.getElementsByTagName("li");
		if(i < list.length) list[i].click();
	},
	alert: function(team, count){
		document.getElementById(team+"_highlight").classList.remove('hidden');
		document.getElementById(team+"_highlight").innerHTML = count;
	},
	unread: function(team){
		document.getElementById(team).classList.add('unread');
	},
	stopAlert: function(team){
		document.getElementById(team+"_highlight").classList.add('hidden');
	},
	stopUnread: function(team){
		document.getElementById(team).classList.remove('unread');
	},
	switchTo: function(id, url){
		leftPane.switchTo(url);
		LeftPane.setActive(id);
	},
	setActive: function(id){
		var list = document.getElementsByTagName("li");
		for(var i=0; i < list.length; i++){
			list[i].classList.remove("active");
		}
		document.getElementById(id).classList.add("active");
	},
	clickNext: function(direction){
		var list = document.getElementsByTagName("li");
		var index = 0;
		for(; index < list.length; index++){
			if (list[index].classList.contains("active")) {
				break;			
			}
		}
		// Go up or down
		index += new Number(direction);
		if (index >= list.length) {
			index = 0;
		} else if (index < 0) {
			index = list.length - 1;
		}
		LeftPane.click(index);
	}
};


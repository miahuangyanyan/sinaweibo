/**
 * Created by Administrator on 10/19/2017.
 */
"object"!=typeof JSON&&(JSON={}),function(){"use strict";function f(a){return 10>a?"0"+a:a}function quote(a){return escapable.lastIndex=0,escapable.test(a)?'"'+a.replace(escapable,function(a){var b=meta[a];return"string"==typeof b?b:"\\u"+("0000"+a.charCodeAt(0).toString(16)).slice(-4)})+'"':'"'+a+'"'}function str(a,b){var c,d,e,f,h,g=gap,i=b[a];switch(i&&"object"==typeof i&&"function"==typeof i.toJSON&&(i=i.toJSON(a)),"function"==typeof rep&&(i=rep.call(b,a,i)),typeof i){case"string":return quote(i);case"number":return isFinite(i)?String(i):"null";case"boolean":case"null":return String(i);case"object":if(!i)return"null";if(gap+=indent,h=[],"[object Array]"===Object.prototype.toString.apply(i)){for(f=i.length,c=0;f>c;c+=1)h[c]=str(c,i)||"null";return e=0===h.length?"[]":gap?"[\n"+gap+h.join(",\n"+gap)+"\n"+g+"]":"["+h.join(",")+"]",gap=g,e}if(rep&&"object"==typeof rep)for(f=rep.length,c=0;f>c;c+=1)"string"==typeof rep[c]&&(d=rep[c],e=str(d,i),e&&h.push(quote(d)+(gap?": ":":")+e));else for(d in i)Object.prototype.hasOwnProperty.call(i,d)&&(e=str(d,i),e&&h.push(quote(d)+(gap?": ":":")+e));return e=0===h.length?"{}":gap?"{\n"+gap+h.join(",\n"+gap)+"\n"+g+"}":"{"+h.join(",")+"}",gap=g,e}}"function"!=typeof Date.prototype.toJSON&&(Date.prototype.toJSON=function(){return isFinite(this.valueOf())?this.getUTCFullYear()+"-"+f(this.getUTCMonth()+1)+"-"+f(this.getUTCDate())+"T"+f(this.getUTCHours())+":"+f(this.getUTCMinutes())+":"+f(this.getUTCSeconds())+"Z":null},String.prototype.toJSON=Number.prototype.toJSON=Boolean.prototype.toJSON=function(){return this.valueOf()});var cx,escapable,gap,indent,meta,rep;"function"!=typeof JSON.stringify&&(escapable=/[\\\"\x00-\x1f\x7f-\x9f\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,meta={"\b":"\\b","	":"\\t","\n":"\\n","\f":"\\f","\r":"\\r",'"':'\\"',"\\":"\\\\"},JSON.stringify=function(a,b,c){var d;if(gap="",indent="","number"==typeof c)for(d=0;c>d;d+=1)indent+=" ";else"string"==typeof c&&(indent=c);if(rep=b,b&&"function"!=typeof b&&("object"!=typeof b||"number"!=typeof b.length))throw new Error("JSON.stringify");return str("",{"":a})}),"function"!=typeof JSON.parse&&(cx=/[\u0000\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,JSON.parse=function(text,reviver){function walk(a,b){var c,d,e=a[b];if(e&&"object"==typeof e)for(c in e)Object.prototype.hasOwnProperty.call(e,c)&&(d=walk(e,c),void 0!==d?e[c]=d:delete e[c]);return reviver.call(a,b,e)}var j;if(text=String(text),cx.lastIndex=0,cx.test(text)&&(text=text.replace(cx,function(a){return"\\u"+("0000"+a.charCodeAt(0).toString(16)).slice(-4)})),/^[\],:{}\s]*$/.test(text.replace(/\\(?:["\\\/bfnrt]|u[0-9a-fA-F]{4})/g,"@").replace(/"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g,"]").replace(/(?:^|:|,)(?:\s*\[)+/g,"")))return j=eval("("+text+")"),"function"==typeof reviver?walk({"":j},""):j;throw new SyntaxError("JSON.parse")})}();
function category(){
	this.tagListConf = {
		'type':false,
		'country':false,
		'year':false
	};
	this.typeNode = $("[node-type='category_type']");
	this.countryNode = $("[node-type='category_country']");
	this.yearNode = $("[node-type='category_year']");
	this.typeList = $("[node-type='type_list']");
	this.countryList = $("[node-type='country_list']");
	this.yearList = $("[node-type='year_list']");
	this.cutTypeList = $("[node-type='cut_type_list']");
	this.cutCountryList = $("[node-type='cut_country_list']");
	this.cutYearList = $("[node-type='cut_year_list']");
	this.tagList = $("[node-type='tag_list']");
	this.deleteNode = "[node-type='delete_tag']";
	this.showListNode = $("[node-type='show_list']");
	this.hideListNode = $("[node-type='hide_list']");
	this.listContent = $("[node-type='list_content']");
	this.typeTag = 0;
	this.countryTag = 0;
	this.yearTag = 0;
	this.total = 0;
	this.data = [];
}

category.prototype = {
	init:function(){
		this.page_obj = new page();
		this.initList();
		this.bind();
	},
	bind:function(){
		this.typeNodeBind();
		this.countryNodeBind();
		this.yearNodeBind();
		this.toggleListBind();
		this.deleteTagBind();
	},
	initList:function(){
		this.getData(1,21,this);
	},
	getList:function(){
		var self = this;
		var url = 'http://movie.weibo.com/movie/webajax/category';
		$.post(url, {type:this.typeTag, country:this.countryTag, year:this.yearTag, page: this.page_obj.currentPage}, function(res){
			self.total = res.data.total;
			self.data = res.data.list;
			self.setData();
			self.getData(1,21,self);
		},'json');
	},
	setData:function(){
		this.page_obj.init(this.total);
		this.page_obj.get();
		this.page_obj.bind(this.getData,this);
	},
	getData:function(page,perNum,category){
		var url = 'http://movie.weibo.com/movie/webajax/category';
		$.post(url, {type:category.typeTag, country:category.countryTag, year:category.yearTag, page: category.page_obj.currentPage}, function(res){
        	category.listContent.empty();
     	 	if( res.data.list != null ){
    	    	var list = res.data.list;
        		for( var i = 0; i < 21; i++){
       	   		 	if( list[i] != undefined ){
           		     	category.renderTemplate('movie',list[i],function(html){
           		         	category.listContent.append(html);
           		     	});
           		 	}
        		}
       		}
		},'json');
	},
	renderTemplate:function(templateId,data,callback){
        template.openTag = '{_';
        template.closeTag = '_}';
        var html = template.render(templateId,{data:data});
        callback.call(this.renderData,html);
    },
	deleteTagBind:function(){
		var self = this;
		this.tagList.delegate(this.deleteNode, 'click', function() {
			var element = $(this);
			var type = element.attr('type');
			self.tagListConf[type] = false;
			self.tagDisable(type);
			element.remove();
			self.renderTagList();
		});
	},
	tagDisable:function(type){
		switch(type){
			case 'type':
				this.typeTag = 0;
				break;
			case 'country':
				this.countryTag = 0;
				break;
			case 'year':
				this.yearTag = 0;
				break;
		}
	},
	toggleListBind:function(){
		this.showListNode.click(function(){
			var element = $(this).closest('div');
			element.hide().prev().show();
		});
		this.hideListNode.click(function(){
			var element = $(this).closest('div');
			element.hide().next().show();
		})
	},
	typeNodeBind:function(){
		var self = this;
		this.typeNode.click(function(){
			var element = $(this);
			var dictId = element.attr('dict-id');
			var name = element.text();
			self.tagListConf.type = true;
			self.addTag(name, 'type');
			self.typeTag = dictId;
			self.renderTagList();
		})
	},
	countryNodeBind:function(){
		var self = this;
		this.countryNode.click(function(){
			var element = $(this);
			var dictId = element.attr('dict-id');
			var name = element.text();
			self.tagListConf.country = true;
			self.addTag(name, 'country');
			self.countryTag = dictId;
			self.renderTagList();
		})
	},
	yearNodeBind:function(){
		var self = this;
		this.yearNode.click(function(){
			var element = $(this);
			var dictId = element.attr('dict-id');
			var name = element.text();
			self.tagListConf.year = true;
			self.addTag(name, 'year');
			self.yearTag = dictId;
			self.renderTagList();
		})
	},
	addTag:function(name, type){
		var tag = '<li node-type="delete_tag" type="'+ type +'"><a class="btn_classify" href="javascript:void(0);">'+ name +'<b class="icon-font">&#xf101;</b></a></li>';
		this.tagList.append(tag);
	},
	renderTagList:function(){
		this.renderTypeList();
		this.renderCountryList();
		this.renderYearList();
		this.getList();
	},
	renderTypeList:function(){
		this.tagListConf.type ? this.hideTypeList() : this.showTypeList();
	},
	hideTypeList:function(){
		this.typeList.hide();
		this.cutTypeList.hide();
	},
	showTypeList:function(){
		this.typeList.hide();
		this.cutTypeList.show();
	},
	renderCountryList:function(){
		this.tagListConf.country ? this.hideCountryList() : this.showCountryList();
	},
	hideCountryList:function(){
		this.countryList.hide();
		this.cutCountryList.hide();
	},
	showCountryList:function(){
		this.countryList.hide();
		this.cutCountryList.show();
	},
	renderYearList:function(){
		this.tagListConf.year ? this.hideYearList() : this.showYearList();
	},
	hideYearList:function(){
		this.yearList.hide();
		this.cutYearList.hide();
	},
	showYearList:function(){
		this.yearList.hide();
		this.cutYearList.show();
	}
}

function page(){
	this.total = 0;
	this.totalPage = 0;
	this.currentPage = 1;
	this.perNum = 21;
	this.showPage = 5;
	this.prevPageBtn = '<a node-type="page_prev" href="javascript:void(0);" class="page prev S_txt1 S_line1">上一页</a>';
	this.nextPageBtn = '<a node-type="page_next" href="javascript:void(0);" class="page next S_txt1 S_line1">下一页</a>';
	this.currentPageBtn = '<a node-type="page_num" href="javascript:void(0);" class="page S_txt1 page_dis">';
	this.morePrevBtn = '<a node-type="page_more_prev" href="javascript:void(0);" class="page S_txt2 page_dis">...</a>';
	this.moreNextBtn = '<a node-type="page_more_next" href="javascript:void(0);" class="page S_txt2 page_dis">...</a>';
	this.pageComponentStr = '';
	this.pageContent = $("[node-type='page_content']");
	this.nextPageNode = "[node-type='page_next']";
	this.prevPageNode = "[node-type='page_prev']";
	this.morePrevNode = "[node-type='page_more_prev']";
	this.moreNextNode = "[node-type='page_more_next']";
	this.pageToNode = "[node-type='page_to']";
}

page.prototype = {
	init:function(total){
		this.total = total;
		this.totalPage = Math.ceil(total / this.perNum);
		this.currentPage = 1;	
	},
	bind:function(callback,category){
		var self = this;
		this.pageContent.undelegate('click').delegate(this.nextPageNode, 'click', function() {
			self.currentPage++;
			callback(self.currentPage,self.perNum,category);
			self.get();
		})
		.delegate(this.prevPageNode, 'click', function(){
			self.currentPage--;
			callback(self.currentPage,self.perNum,category);
			self.get();
		})
		.delegate(this.pageToNode, 'click', function() {
			self.currentPage = parseInt($(this).text());
			callback(self.currentPage,self.perNum,category);
			self.get();
		})
		.delegate(this.moreNextNode, 'click', function(){
			self.currentPage += 3;
			callback(self.currentPage,self.perNum,category);
			self.get();
		})
		.delegate(this.morePrevNode, 'click', function(){
			self.currentPage -= 3;
			callback(self.currentPage,self.perNum,category);
			self.get();
		});
	},
	scrollUp:function(){
		$(document).scrollTop(0);
	},
	get:function(){
		this.render();
		this.pageContent.empty().append(this.pageComponentStr);
		this.scrollUp();
	},
	render:function(){
		if( this.totalPage == 1 ){
			this.pageComponentStr = '';
		}else if( this.totalPage <= this.showPage + 2 ){
			this.renderComplete();
		}else{
			this.renderSome();
		}
	},
	setPage:function(page){
		this.currentPage = page;
	},
	prevPageValidate:function(){
		return ( this.currentPage <= 1 ) ? false : true;
	},
	nextPageValidate:function(){
		return ( this.currentPage >= this.totalPage ) ? false : true;
	},
	renderComplete:function(){
		var str = '';
		var	commonStr = '';
		for( var i = 1; i <= this.totalPage; i++ ){
			if( i == this.currentPage ){
				str += this.currentPageBtn + i + '</a>';
			}else{
				commonStr = '<a node-type="page_to" href="javascript:void(0);" class="page S_txt1">'+ i +'</a>';
				str += commonStr;
			}
		}
		this.pageComponentStr = this.renderPageBtn(str);
		//this.pageComponentStr = this.wrapPage(str);
	},
	renderSome:function(){
		var str = '';
		var	commonStr = '';
		if( this.currentPage < this.showPage ){
			for( var i = 1; i <= this.showPage+1; i++ ){
				if( i == this.currentPage ){
					str += this.currentPageBtn + i + '</a>';
				}else{
					commonStr = '<a node-type="page_to" href="javascript:void(0);" class="page S_txt1">'+ i +'</a>';
					str += commonStr;
				}
			}
			str += this.moreNextBtn;
			str += '<a node-type="page_to" href="javascript:void(0);" class="page S_txt1">'+ this.totalPage +'</a>';
		}else if( this.currentPage >= this.totalPage + 2 - this.showPage ){
			var start = this.totalPage - this.showPage;
			for( var i = start; i <= this.totalPage; i++ ){
				if( i == this.currentPage ){
					str += this.currentPageBtn + i + '</a>';
				}else{
					commonStr = '<a node-type="page_to" href="javascript:void(0);" class="page S_txt1">'+ i +'</a>';
					str += commonStr;
				}
			}
			str = this.morePrevBtn + str;
			str = '<a node-type="page_to" href="javascript:void(0);" class="page S_txt1">1</a>' + str;
		}else{
			var start = this.currentPage - 2;
			var end = this.currentPage + 2;
			for( var i = start; i <= end; i++ ){
				if( i == this.currentPage ){
					str += this.currentPageBtn + i + '</a>';
				}else{
					commonStr = '<a node-type="page_to" href="javascript:void(0);" class="page S_txt1">'+ i +'</a>';
					str += commonStr;
				}
			}
			str = this.morePrevBtn + str;
			str = '<a node-type="page_to" href="javascript:void(0);" class="page S_txt1">1</a>' + str;
			str += this.moreNextBtn;
			str += '<a node-type="page_to" href="javascript:void(0);" class="page S_txt1">'+ this.totalPage +'</a>';
		}
		this.pageComponentStr = this.renderPageBtn(str);
		//this.pageComponentStr = this.wrapPage(str);
	},
	renderPageBtn:function(str){
		if( this.prevPageValidate() ){
			str = this.prevPageBtn + str;
		}
		if( this.nextPageValidate() ){
			str += this.nextPageBtn;
		}
		return str;
	}

}

var category_obj = new category();
category_obj.init();
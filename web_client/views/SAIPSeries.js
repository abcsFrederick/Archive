import View from 'girder/views/View';
import seriesTemplate from '../templates/seriesTemplate.pug'
import { restRequest } from 'girder/rest';
//import SAIPSeriesView from '../SAIP/SAIPSeries';
import events from '../events';
var SAIPSeries = View.extend({
	events:{
		'click a.SAIP-folder-list-link-series':function (event) {
            event.preventDefault();
            this.itemSelected(event.currentTarget.getAttribute('series-id'))
        },
        'click .SAIP-list-checkbox-series':function(e){
        	events.trigger('ssr:chooseFolderItem',e)
        }
	},
	initialize(setting){
		this.hierarchyBreadcrumbView = setting.hierarchyBreadcrumbView;
		this.currentUser=setting.currentUser;
		this.parentCheckboxFlag=setting.parentCheckbox;
		this.seriesFolder = setting.seriesFolder;
		//console.log(this.seriesFolder)
		this.$el.html(seriesTemplate({
			folders:this.seriesFolder,
			parentCheckboxFlag:this.parentCheckboxFlag
			})
		);
	},
	itemSelected(e){

	}
});

export default SAIPSeries;
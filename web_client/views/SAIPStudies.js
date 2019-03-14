import View from 'girder/views/View';
import studiesTemplate from '../templates/studiesTemplate.pug'
import { restRequest } from 'girder/rest';
import SAIPSeriesView from './SAIPSeries';
import events from '../events';
import SAIPHierarchyBreadcrumbView from './SAIPHierarchyBreadcrumbView';
var SAIPPatients = View.extend({
	events:{
		'click a.SAIP-folder-list-link-studies':function (event) {
            event.preventDefault();
            this.breadcrumbObj = {'object':{'name':event.currentTarget.getAttribute('name')},'type':'study'};
            let parentCheckbox =event.currentTarget.parentElement.children[0].checked;
            this.showSeries(event.currentTarget.getAttribute('study-id'),parentCheckbox)
        },
        'click .SAIP-list-checkbox-studies':function(e){
        	// events.trigger('ssr:chooseFolderItem',e)
        	console.log(e.currentTarget.getAttribute('s-study-id'));
        	this.selectecStudyId = e.currentTarget.getAttribute('s-study-id');
        	this.selectionWindow(e.currentTarget.getAttribute('s-study-id'))
        }
	},
	initialize(setting){
		this.selectecStudyId;
		this.hierarchyBreadcrumbView = setting.hierarchyBreadcrumbView;
		this.parentCheckboxFlag=setting.parentCheckbox;
		this.currentUser=setting.currentUser;
		this.studiesFolder = setting.studiesFolder;
		this.SAIPHierarchyBreadcrumbObjects=setting.SAIPHierarchyBreadcrumbObjects;
		console.log(this.studiesFolder)
		this.$el.html(studiesTemplate({
			folders:this.studiesFolder,
			parentCheckboxFlag:this.parentCheckboxFlag
			})
		);
	},
	selectionWindow(e){
		restRequest({
			url:'SAIP/'+e+'/series'	
		}).then((col)=>{
			console.log('from selectionWindow');
			console.log(col);
			events.trigger('preview:selectionWindow',col)
		});
	},
	showSeries(e,parentCheckbox){
	//	console.log(e)
		restRequest({
			url:'SAIP/'+e+'/series'	
		}).then((col)=>{
			// console.log('series');
			// console.log(col);
			// this.SAIPHierarchyBreadcrumbObjects.push(this.breadcrumbObj)
			this.new = true;
			this.SAIPHierarchyBreadcrumbObjects.forEach(_.bind(function(obj) {
			  if (this.breadcrumbObj['type']===obj['type'])
			  {
			  	this.new = false;
			  }
			},this));

			if(this.new){
				this.SAIPHierarchyBreadcrumbObjects.push(this.breadcrumbObj)
			}else{
				this.SAIPHierarchyBreadcrumbObjects.forEach(_.bind(function(obj) {
				  if (this.breadcrumbObj['type']===obj['type'])
				  {
				  	obj['object'] = this.breadcrumbObj['object']
				  }
				},this));
			}
			this.hierarchyBreadcrumbView.objects = this.SAIPHierarchyBreadcrumbObjects;
			this.hierarchyBreadcrumbView.render();
			if(this.saipSeriesView){
				this.saipSeriesView.destroy()	//prevent from zombie view
			}
			this.saipSeriesView = new SAIPSeriesView({
				parentView:this,
				parentCheckbox:parentCheckbox,
				currentUser:this.currentUser,
				seriesFolder:col,
				SAIPHierarchyBreadcrumbObjects:this.SAIPHierarchyBreadcrumbObjects,
				hierarchyBreadcrumbView:this.hierarchyBreadcrumbView
			});
			$('#projects .g-folder-list-container .g-folder-list-studies').hide();
			$('#projects .g-folder-list-container .g-folder-list-series').html(this.saipSeriesView.el)
			$('#projects .g-folder-list-container .g-folder-list-series').show();
			this.hierarchyBreadcrumbView.on('g:breadcrumbClicked',_.bind(function(idx){
				if(idx === 4)
				{	
					$('#projects .g-folder-list-container > div > div').hide();
					$('#projects .g-folder-list-container .g-folder-list-series').show();
					this.SAIPHierarchyBreadcrumbObjects=this.SAIPHierarchyBreadcrumbObjects.slice(0, idx + 1);
					this.hierarchyBreadcrumbView.objects = this.SAIPHierarchyBreadcrumbObjects;
					this.hierarchyBreadcrumbView.render();
					// if(this.saipSeriesView){
					// 	this.saipSeriesView.destroy()	//prevent from zombie view
					// }
					// this.SAIPHierarchyBreadcrumbObjects=this.SAIPHierarchyBreadcrumbObjects.slice(0, idx + 1);
					// this.saipSeriesView = new SAIPSeriesView({
					// 	parentView:this,
					// 	parentCheckbox:parentCheckbox,
					// 	currentUser:this.currentUser,
					// 	seriesFolder:col,
					// 	SAIPHierarchyBreadcrumbObjects:this.SAIPHierarchyBreadcrumbObjects,
					// 	hierarchyBreadcrumbView:this.hierarchyBreadcrumbView
					// });
					// $('#projects .g-folder-list-container').html(this.saipSeriesView.el)
					// this.hierarchyBreadcrumbView.objects = this.SAIPHierarchyBreadcrumbObjects;
					// this.hierarchyBreadcrumbView.render();
				}
			},this));
			// if(this.hierarchyBreadcrumbView){
			// 	this.hierarchyBreadcrumbView.destroy()	//prevent from zombie view
			// }
			// this.hierarchyBreadcrumbView = new SAIPHierarchyBreadcrumbView({
			// 	parentView:this,
			// 	objects:this.SAIPHierarchyBreadcrumbObjects
			// });
			//$('#projects .g-hierarchy-breadcrumb-bar').html(this.hierarchyBreadcrumbView.el)
		});
	}
});

export default SAIPPatients;
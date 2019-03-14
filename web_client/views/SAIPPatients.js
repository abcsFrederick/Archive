import View from 'girder/views/View';
import patientsTemplate from '../templates/patientsTemplate.pug'
import { restRequest } from 'girder/rest';
import SAIPStudiesView from './SAIPStudies';
import events from '../events';
import SAIPHierarchyBreadcrumbView from './SAIPHierarchyBreadcrumbView';
var SAIPPatients = View.extend({
	events:{
		'click a.SAIP-folder-list-link-patients':function (event) {
            event.preventDefault();
            this.breadcrumbObj = {'object':{'name':event.currentTarget.getAttribute('name')},'type':'patient'};
            let parentCheckbox =event.currentTarget.parentElement.children[0].checked;
            this.showStudies(event.currentTarget.getAttribute('pat-id'),parentCheckbox)
        },
        'click .SAIP-list-checkbox-patients':function(e){
        	events.trigger('ssr:chooseFolderItem',e)
        }
	},
	initialize(setting){
		this.hierarchyBreadcrumbView = setting.hierarchyBreadcrumbView;
		this.parentCheckboxFlag=setting.parentCheckbox;
		this.currentUser=setting.currentUser;
		this.patientsFolder = setting.patientsFolder;
		this.SAIPHierarchyBreadcrumbObjects=setting.SAIPHierarchyBreadcrumbObjects;
		//console.log(this.patientsFolder)
		this.$el.html(patientsTemplate({
			folders:this.patientsFolder,
			parentCheckboxFlag:this.parentCheckboxFlag
			})
		);
	},
	showStudies(e,parentCheckbox){
		restRequest({
			url:'SAIP/'+e+'/studies'	
		}).then((col)=>{
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
				  // if (obj['type'] === 'series')
				  // {
				  // 	delete obj;
				  // }
				},this));
			}
			// this.SAIPHierarchyBreadcrumbObjects.push(this.breadcrumbObj)
			this.hierarchyBreadcrumbView.objects = this.SAIPHierarchyBreadcrumbObjects;
			this.hierarchyBreadcrumbView.render();
			if(this.saipStudiesView){
				this.saipStudiesView.destroy()	//prevent from zombie view
			}
			this.saipStudiesView = new SAIPStudiesView({
				parentView:this,
				parentCheckbox:parentCheckbox,
				currentUser:this.currentUser,
				studiesFolder:col,
				SAIPHierarchyBreadcrumbObjects:this.SAIPHierarchyBreadcrumbObjects,
				hierarchyBreadcrumbView:this.hierarchyBreadcrumbView
			});
			$('#projects .g-folder-list-container .g-folder-list-patients').hide();
			$('#projects .g-folder-list-container .g-folder-list-studies').html(this.saipStudiesView.el)
			$('#projects .g-folder-list-container .g-folder-list-studies').show();
			this.hierarchyBreadcrumbView.on('g:breadcrumbClicked',_.bind(function(idx){
				if(idx === 3)
				{	
					$('#projects .g-folder-list-container > div > div').hide();
					$('#projects .g-folder-list-container .g-folder-list-studies').show();
					this.SAIPHierarchyBreadcrumbObjects=this.SAIPHierarchyBreadcrumbObjects.slice(0, idx + 1);
					this.hierarchyBreadcrumbView.objects = this.SAIPHierarchyBreadcrumbObjects;
					this.hierarchyBreadcrumbView.render();
					// if(this.saipStudiesView){
					// 	this.saipStudiesView.destroy()	//prevent from zombie view
					// }
					// this.SAIPHierarchyBreadcrumbObjects=this.SAIPHierarchyBreadcrumbObjects.slice(0, idx + 1);
					// this.saipStudiesView = new SAIPStudiesView({
					// 	parentView:this,
					// 	parentCheckbox:parentCheckbox,
					// 	currentUser:this.currentUser,
					// 	studiesFolder:col,
					// 	SAIPHierarchyBreadcrumbObjects:this.SAIPHierarchyBreadcrumbObjects,
					// 	hierarchyBreadcrumbView:this.hierarchyBreadcrumbView
					// });
					// $('#projects .g-folder-list-container').html(this.saipStudiesView.el)
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
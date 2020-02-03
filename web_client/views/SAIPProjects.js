import View from 'girder/views/View';
import projectsTemplate from '../templates/projectsTemplate.pug'
import { restRequest } from 'girder/rest';
import SAIPExperimentsView from './SAIPExperiments';
import events from '../events';
import SAIPHierarchyBreadcrumbView from './SAIPHierarchyBreadcrumbView';
var SAIPProjects = View.extend({
	events:{
		'click a.SAIP-folder-list-link-projects':function (event) {
      event.preventDefault();
      this.breadcrumbObj = {'object':{'name':event.currentTarget.getAttribute('name')},'type':'project'};
      let parentCheckbox = event.currentTarget.parentElement.children[0].checked;
      this.showExperiments(event.currentTarget.getAttribute('pro-id'),parentCheckbox);
    },
    'click .SAIP-list-checkbox-projects':function(e){
    	events.trigger('ssr:chooseFolderItem',e)
    }
	},
	initialize(setting){

		this.hierarchyBreadcrumbView = setting.hierarchyBreadcrumbView;
		this.currentUser=setting.currentUser;
		this.projectsFolder = setting.projectsFolder;
		this.SAIPHierarchyBreadcrumbObjects=setting.SAIPHierarchyBreadcrumbObjects;

		this.$el.html(projectsTemplate({
			folders:this.projectsFolder
			})
		);
	},
	showExperiments(e,parentCheckbox){
		restRequest({
			url:'SAIP/'+e+'/experiments'	
		}).then((col)=>{
			// console.log('project SAIPHierarchyBreadcrumbObjects');
			// console.log(this.SAIPHierarchyBreadcrumbObjects);
			// console.log(this.breadcrumbObj);
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
			// this.SAIPHierarchyBreadcrumbObjects.push(this.breadcrumbObj)
			// console.log('project SAIPHierarchyBreadcrumbObjects push');
			// console.log(this.SAIPHierarchyBreadcrumbObjects);
			this.hierarchyBreadcrumbView.objects = this.SAIPHierarchyBreadcrumbObjects;
			this.hierarchyBreadcrumbView.render();
			if(this.saipExperimentsView){
				this.saipExperimentsView.destroy()	//prevent from zombie view
			}
			// console.log(this.breadcrumbObj);
			// console.log('after');
			// console.log(this.SAIPHierarchyBreadcrumbObjects);
			this.saipExperimentsView = new SAIPExperimentsView({
				parentView:this,
				// parentCheckbox:parentCheckbox,
				currentUser:this.currentUser,
				experimentsFolder:col,
				SAIPHierarchyBreadcrumbObjects:this.SAIPHierarchyBreadcrumbObjects,
				hierarchyBreadcrumbView:this.hierarchyBreadcrumbView
			});
			$('#projects .g-folder-list-container .g-folder-list-projects').hide();
			$('#projects .g-folder-list-container .g-folder-list-experiments').html(this.saipExperimentsView.el)
			$('#projects .g-folder-list-container .g-folder-list-experiments').show();
			
			this.hierarchyBreadcrumbView.on('g:breadcrumbClicked',_.bind(function(idx){
				if(idx === 1)
				{	
					$('#projects .g-folder-list-container > div > div').hide();
					$('#projects .g-folder-list-container .g-folder-list-experiments').show();
					this.SAIPHierarchyBreadcrumbObjects=this.SAIPHierarchyBreadcrumbObjects.slice(0, idx + 1);
					this.hierarchyBreadcrumbView.objects = this.SAIPHierarchyBreadcrumbObjects;
					this.hierarchyBreadcrumbView.render();
					// this.hierarchyBreadcrumbView.render();
					// console.log(idx)
					// if(this.saipExperimentsView){
					// 	this.saipExperimentsView.destroy()	//prevent from zombie view
					// }
					// this.SAIPHierarchyBreadcrumbObjects=this.SAIPHierarchyBreadcrumbObjects.slice(0, idx + 1);
					// this.saipExperimentsView = new SAIPExperimentsView({
					// 	parentView:this,
					// 	parentCheckbox:parentCheckbox,
					// 	currentUser:this.currentUser,
					// 	experimentsFolder:col,
					// 	SAIPHierarchyBreadcrumbObjects:this.SAIPHierarchyBreadcrumbObjects,
					// 	hierarchyBreadcrumbView:this.hierarchyBreadcrumbView
					// });
					// $('#projects .g-folder-list-container').html(this.saipExperimentsView.el)
					// this.hierarchyBreadcrumbView.objects = this.SAIPHierarchyBreadcrumbObjects;
					// this.hierarchyBreadcrumbView.render();
				}
			},this));
		});
	}
});

export default SAIPProjects;
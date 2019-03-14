import View from 'girder/views/View';
import experimentsTemplate from '../templates/experimentsTemplate.pug'
import { restRequest } from 'girder/rest';
import SAIPPatientsView from './SAIPPatients';
import events from '../events';
import SAIPHierarchyBreadcrumbView from './SAIPHierarchyBreadcrumbView';
var SAIPExperiments = View.extend({
	events:{
		'click a.SAIP-folder-list-link-experiments':function (event) {
            event.preventDefault();
            this.breadcrumbObj = {'object':{'name':event.currentTarget.getAttribute('name')},'type':'experiment'};
            console.log(this.SAIPHierarchyBreadcrumbObjects)
            let parentCheckbox =event.currentTarget.parentElement.children[0].checked;
            this.showPatients(event.currentTarget.getAttribute('exp-id'),parentCheckbox)
        },
        'click .SAIP-list-checkbox-patients':function(e){
        	events.trigger('ssr:chooseFolderItem',e)
        }
	},
	initialize(setting){
		this.hierarchyBreadcrumbView = setting.hierarchyBreadcrumbView;
		console.log(this.hierarchyBreadcrumbView)
		this.parentCheckboxFlag=setting.parentCheckbox;
		this.currentUser=setting.currentUser;
		this.experimentsFolder = setting.experimentsFolder;
		this.SAIPHierarchyBreadcrumbObjects=setting.SAIPHierarchyBreadcrumbObjects;
		//console.log(this.parentCheckboxFlag)
		this.$el.html(experimentsTemplate({
			folders:this.experimentsFolder,
			parentCheckboxFlag:this.parentCheckboxFlag
			})
		);
	},
	showPatients(e,parentCheckbox){
		restRequest({
			url:'SAIP/'+e+'/patients'	
		}).then(_.bind((col)=>{

			this.new = true;
			console.log('pause')
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
				  console.log(obj)
				  // if (obj['type'] === 'studies')
				  // {
				  // 	delete obj;
				  // }
				  // if (obj['type'] === 'series')
				  // {
				  // 	delete obj;
				  // }


				},this));
			}

      // this.SAIPHierarchyBreadcrumbObjects.push(this.breadcrumbObj)
      
			this.hierarchyBreadcrumbView.objects = this.SAIPHierarchyBreadcrumbObjects;
			this.hierarchyBreadcrumbView.render();
			if(this.saipPatientsView){
				this.saipPatientsView.destroy()	//prevent from zombie view
			}


			this.saipPatientsView = new SAIPPatientsView({
				parentView:this,
				parentCheckbox:parentCheckbox,
				currentUser:this.currentUser,
				patientsFolder:col,
				SAIPHierarchyBreadcrumbObjects:this.SAIPHierarchyBreadcrumbObjects,
				hierarchyBreadcrumbView:this.hierarchyBreadcrumbView
			});
			$('#projects .g-folder-list-container .g-folder-list-experiments').hide();
			$('#projects .g-folder-list-container .g-folder-list-patients').html(this.saipPatientsView.el)
			$('#projects .g-folder-list-container .g-folder-list-patients').show();
			this.hierarchyBreadcrumbView.on('g:breadcrumbClicked',_.bind(function(idx){
				if(idx === 2)
				{	
					$('#projects .g-folder-list-container > div > div').hide();
					$('#projects .g-folder-list-container .g-folder-list-patients').show();
					this.SAIPHierarchyBreadcrumbObjects=this.SAIPHierarchyBreadcrumbObjects.slice(0, idx + 1);
					this.hierarchyBreadcrumbView.objects = this.SAIPHierarchyBreadcrumbObjects;
					this.hierarchyBreadcrumbView.render();
					// if(this.saipPatientsView){
					// 	this.saipPatientsView.destroy()	//prevent from zombie view
					// }
					// this.SAIPHierarchyBreadcrumbObjects=this.SAIPHierarchyBreadcrumbObjects.slice(0, idx + 1);
					// this.saipPatientsView = new SAIPPatientsView({
					// 	parentView:this,
					// 	parentCheckbox:parentCheckbox,
					// 	currentUser:this.currentUser,
					// 	patientsFolder:col,
					// 	SAIPHierarchyBreadcrumbObjects:this.SAIPHierarchyBreadcrumbObjects,
					// 	hierarchyBreadcrumbView:this.hierarchyBreadcrumbView
					// });
					// $('#projects .g-folder-list-container').html(this.saipPatientsView.el)
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
		},this));
	}
});

export default SAIPExperiments;
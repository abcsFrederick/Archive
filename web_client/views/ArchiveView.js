import View from 'girder/views/View';
import events from 'girder/events';
import SAIPHierarchyBreadcrumbView from './SAIPHierarchyBreadcrumbView';
import SAIPProjectsView from './SAIPProjects';
import { restRequest } from 'girder/rest';
import { getCurrentUser } from 'girder/auth';
import SAIPTemplates from '../templates/archivePage.pug';
import UserModel from 'girder/models/UserModel';

var ArchiveView = View.extend({
    events:{

    },
    initialize(settings) {
        console.log(this.currentUser)
        this.$el.html(SAIPTemplates());
        this.SAIPHierarchyBreadcrumbObjects=[{'object':{'name':'SAIP'},'type':'SAIP'}];
        this.currentUser = getCurrentUser();
        console.log(this.currentUser)
        restRequest({
            url:'SAIP/'+this.currentUser.get('login')+'/projects' 
        }).then((col)=>{
            console.log('21')
            if(this.hierarchyBreadcrumbView){
            this.hierarchyBreadcrumbView.destroy()  //prevent from zombie view
            }
      this.hierarchyBreadcrumbView = new SAIPHierarchyBreadcrumbView({
        parentView:this,
        objects:this.SAIPHierarchyBreadcrumbObjects
      });
      $('#projects .g-hierarchy-breadcrumb-bar').html(this.hierarchyBreadcrumbView.el)

      if(this.saipProjectsView){
        this.saipProjectsView.destroy() //prevent from zombie view
      }
      this.saipProjectsView = new SAIPProjectsView({
        parentView:this,
        currentUser:this.currentUser,
        projectsFolder:col,
        SAIPHierarchyBreadcrumbObjects:this.SAIPHierarchyBreadcrumbObjects,
        hierarchyBreadcrumbView:this.hierarchyBreadcrumbView
      });
      $('#projects .g-folder-list-container').html(this.saipProjectsView.el)
      
      this.hierarchyBreadcrumbView.on('g:breadcrumbClicked',_.bind(function(idx){
        if(idx === 0)
        { 
          console.log(idx)
          this.SAIPHierarchyBreadcrumbObjects=this.SAIPHierarchyBreadcrumbObjects.slice(0, idx + 1);
          if(this.saipProjectsView){
            this.saipProjectsView.destroy() //prevent from zombie view
          }
          this.saipProjectsView = new SAIPProjectsView({
            parentView:this,
            currentUser:this.currentUser,
            projectsFolder:col,
            SAIPHierarchyBreadcrumbObjects:this.SAIPHierarchyBreadcrumbObjects,
            hierarchyBreadcrumbView:this.hierarchyBreadcrumbView
          });
          $('#projects .g-folder-list-container').html(this.saipProjectsView.el)
          this.hierarchyBreadcrumbView.objects = this.SAIPHierarchyBreadcrumbObjects;
          this.hierarchyBreadcrumbView.render();
        }
      },this));
    });
  },
  render(){
    return this;
  }
});

export default ArchiveView;
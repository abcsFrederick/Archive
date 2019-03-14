import Model from 'girder/models/Model';
import Backbone from 'backbone';

var scippyModel = Backbone.Model.extend({
	id:'',
	pat_name:'',
	mod_time:'',
	pat_path:'',
	pat_mrn:''
})

export default scippyModel;
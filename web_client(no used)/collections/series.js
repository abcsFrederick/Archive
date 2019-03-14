import Collection from 'girder/collections/Collection';
//import patientsModel from '../models/patients';

import Backbone from 'backbone';

var seriesCollection =  Backbone.Collection.extend({
	//resourceName:'scippy/allpatients',
//    model: patientsModel,
	initialize(setting){
		this.id = setting.id
	},
	url: function(){
		return 'scippy/'+this.id+'/series'
	},
});

export default seriesCollection;
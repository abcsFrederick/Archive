import Collection from 'girder/collections/Collection';

import patientsModel from '../models/patients';

import Backbone from 'backbone';

var patientsCollection =  Backbone.Collection.extend({
	//resourceName:'scippy/allpatients',
    model: patientsModel,
	url: function(){
		return 'scippy/allpatients'
	},
});

export default patientsCollection;

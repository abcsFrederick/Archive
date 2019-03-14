import View from 'girder/views/View';
import seriesTable from '../templates/seriesTable.pug';
import SeriesCollection from '../collections/series';
import analysis from './analysis/analysis';

import 'datatables.net';
import 'datatables.net-buttons';
var seriesView = View.extend({
	events:{
		'click #seriesTable tbody tr':'analyeseRender'
	},
	initialize(setting){
		this.$el.html(seriesTable())
		this.seriesCollection = new SeriesCollection({
			id:setting.id
		});
		this.studyPath = setting.studyPath;
		this.patientPath = setting.patientPath;
		this.seriesRender();
	},
	seriesRender(){
		this.seriesCollection.fetch({
			xhrFields: {
				  withCredentials: true							// override ajax to send with credential
			},
			success:_.bind(function(res){
				console.log(res.toJSON())
				this.seriesTableView = $('#seriesTable').DataTable({
						data:res.toJSON(),
						rowId:'0',
					    'createdRow': _.bind(function( row, data, dataIndex ) {
						      $(row).attr('source', 'scippy');
						      $(row).attr('path', this.patientPath+'_'+this.studyPath+'_'+data[2]);
						},this),
					    columns: [
					    	{
					    		data:'3'
					    	}
					    ],
					    destroy: true,
						"lengthMenu":[[-1],['ALL']],
						"scrollY": "60vh",
						"scrollCollapse": true,
						"dom":'rt'
				})
			},this)
		})
	},
	analyeseRender(e){
		console.log(e.currentTarget.id);
		console.log($('#analysis'))
		if(this.analysisView){
			this.analysisView.destroy()	//prevent from zombie view
		}
		this.analysisView = new analysis({
			selectedImageQuery:e.currentTarget.getAttribute('path'),
			parentView:this
		});
		$('.analysisContent').html(this.analysisView.el)
	}
});

export default seriesView;

import View from 'girder/views/View';
import studiesTable from '../templates/studiesTable.pug';
import StudyCollection from '../collections/studies';
import SeriesView from './seriesView'
import 'datatables.net';
import 'datatables.net-buttons';
var studiesView = View.extend({
	events:{
		'click #studiesTable tbody tr':'seriesRender'
	},
	initialize(setting){
		this.$el.html(studiesTable())

		this.studyCollection = new StudyCollection({
			id:setting.id
		});
		this.patientPath = setting.patientPath;
		this.seriesDom = setting.seriesDom;
		this.studiesRender();
	},
	studiesRender(){
		this.studyCollection.fetch({
			xhrFields: {
				  withCredentials: true							// override ajax to send with credential
			},
			success:_.bind(function(res){
				console.log(res.toJSON())
				this.studiesTableView = $('#studiesTable').DataTable({
						data:res.toJSON(),
					    rowId: '0',
					    'createdRow': function( row, data, dataIndex ) {
						      $(row).attr('path', data[2]);
						},
					    columns: [
					    	{
					    		data:'1'
					    	},
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
	seriesRender(e){
		console.log(this.patientPath)
		console.log(e.currentTarget)
		if(this.seriesView){
			this.seriesView.destroy()	//prevent from zombie view
		}
		this.seriesView = new SeriesView({
			id:e.currentTarget.id,
			patientPath:this.patientPath,
			studyPath:e.currentTarget.getAttribute('path'),
			parentView:this
		})
		this.seriesDom.html(this.seriesView.el)
	}
});

export default studiesView;

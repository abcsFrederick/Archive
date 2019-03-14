import View from 'girder/views/View';
import overallTable from '../templates/overallTable.pug';
import PatientCollection from '../collections/patients';
import StudiesView from './studiesView'
import 'datatables.net';
import 'datatables.net-buttons';
var scippyView = View.extend({
	events:{
		'click #patientsTable tbody tr':'studiesRender'
	},
	initialize(){
		this.$el.html(overallTable())
		this.patientCollection = new PatientCollection();
		this.patientsRender();
	},
	render(){},
	patientsRender(){
		this.patientCollection.fetch({
			xhrFields: {
				  withCredentials: true							// override ajax to send with credential
			},
			success:_.bind(function(res){
				console.log(res)
				this.patientsTableView = $('#patientsTable').DataTable({
						data:res.toJSON(),
					    rowId: '0',
					    'createdRow': function( row, data, dataIndex ) {
						      $(row).attr('path', data[3]);
						},
					    columns: [
					    	{
					    		data:'1'
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
	studiesRender(e){
		console.log(e.currentTarget.id);
		//window.tst=e.currentTarget;
		if(this.studiesView){
			this.studiesView.destroy()	//prevent from zombie view
		}
		this.studiesView = new StudiesView({
			id:e.currentTarget.id,
			patientPath:e.currentTarget.getAttribute('path'),
			parentView:this,
			seriesDom:$('#series')
		})
		$('#studies').html(this.studiesView.el)
	}
});

export default scippyView;

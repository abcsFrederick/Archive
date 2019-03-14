import View from 'girder/views/View';
import analysisTable from '../../templates/analysis/analysisTable.pug';
import { restRequest } from 'girder/rest';
import 'datatables.net';
import 'datatables.net-buttons';
var analysis = View.extend({
	events:{
		'change #analysisSelection':'selectAnalysis'
	},
	initialize(setting){
		this.selectedImageQuery = setting.selectedImageQuery;
		this.$el.html(analysisTable());
		restRequest({
                url: 'slicer_cli_web_SSR/slicer_cli_web_SSR/docker_image'
            }).then(_.bind((analyses) => {
            	console.log(analyses);
              	this.analyses=analyses
                return null;
            },this));
	},
	selectAnalysis(e){
		this.analysesTable = []
		
		//console.log($('#'+e.currentTarget.id).val());
		this.selectionTag = $('#'+e.currentTarget.id).val();
		for(let a=0;a<_.keys(this.analyses).length;a++){
			this.analysesInfo = new Object();
			//console.log(this.analyses[_.keys(this.analyses)[a]])
			this.imageName = _.keys(this.analyses)[a];
			this.images = this.analyses[this.imageName];
			window.tst=this.imageName;
			for(let b=0;b<_.keys(this.images).length;b++){
				this.tagName = _.keys(this.images)[b]
				this.tasks = this.images[this.tagName]
				if(this.tagName==this.selectionTag)
				{
					this.analysesInfo.imageName = this.imageName;
					this.analysesInfo.tasks = this.tasks;
					this.analysesTable.push(this.analysesInfo)
				}
			}
		}
		console.log(this.analysesTable)
		this.analysisTable=$('#analysisTable').DataTable({
			data:this.analysesTable,
			columns: [
		    	{
		    		data:'imageName'
		    	},
		    	{
		    		"targets": 1,
		            "render": _.bind(function ( data, type, full, meta ) {
		            	let result=' ';
		            	for(let a=0;a<_.keys(full.tasks).length;a++){
		            		let analysesQuery;
		            		console.log(full.tasks[_.keys(full.tasks)[a]].run);
		            		analysesQuery=full.tasks[_.keys(full.tasks)[a]].run.replace(/\/run$/, '');
		            		result += '<li><a href="http://localhost:8888/'+this.selectionTag+'#?scippyDB='+this.selectedImageQuery+'&analysis'+this.selectionTag+'='+analysesQuery +'">'+_.keys(full.tasks)[a]+'</a></li>'+'\n';
		            	}
		            	return result;
		            },this)
		    	}
		    ],
			destroy: true,
			"lengthMenu":[[-1],['ALL']],
			"scrollY": "60vh",
			"scrollCollapse": true,
			"dom":'rt'
		});
	}
});

export default analysis;
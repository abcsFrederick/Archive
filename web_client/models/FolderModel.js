import _ from 'underscore';

import AccessControlledModel from 'girder/models/AccessControlledModel';
import MetadataMixin from 'girder/models/MetadataMixin';
import { restRequest } from 'girder/rest';

var FolderModel = AccessControlledModel.extend({
    resourceName: 'Archive',
    archive: null,
    type: null,

    fetch: function (opts) {
        if (this.altUrl === null && this.resourceName === null) {
            throw new Error('An altUrl or resourceName must be set on the Model.');
        }
        opts = opts || {};
        var restOpts = {
            url: `${this.altUrl || this.resourceName}/${this.get('archive')}/${this.get('type')}`
        };
        if (opts.ignoreError) {
            restOpts.error = null;
        }
        if (opts.data) {
            restOpts.data = opts.data;
        }
        return restRequest(restOpts).done((resp) => {
            this.set(resp);
            if (opts.extraPath) {
                this.trigger('g:fetched.' + opts.extraPath);
            } else {
                this.trigger('g:fetched');
            }
        }).fail((err) => {
            this.trigger('g:error', err);
        });
    }
});

_.extend(FolderModel.prototype, MetadataMixin);

export default FolderModel;

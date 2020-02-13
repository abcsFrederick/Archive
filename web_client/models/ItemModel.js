import _ from 'underscore';

import AccessControlledModel from 'girder/models/AccessControlledModel';
import MetadataMixin from 'girder/models/MetadataMixin';
import { restRequest } from 'girder/rest';

import FileCollection from '../collections/FileCollection';

var ItemModel = AccessControlledModel.extend({
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
    },
    getSlices: function (id) {
        return restRequest({
            url: `${this.altUrl || this.resourceName}/${this.get('archive')}/slices`,
            data: {id: id}
        }).then((resp) => {
            let fileCollection = new FileCollection(resp);
            this.trigger('archive:slices', fileCollection);
            return fileCollection;
        }).fail((err) => {
            this.trigger('g:error', err);
        });
    }
});

_.extend(ItemModel.prototype, MetadataMixin);

export default ItemModel;

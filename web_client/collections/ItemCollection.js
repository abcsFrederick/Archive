import Collection from 'girder/collections/Collection';
import ItemModel from '../models/ItemModel';

var FolderCollection = Collection.extend({
    resourceName: 'Archive',
    model: ItemModel,

    pageLimit: 10000,

    rename: function (opts) {
        this.resourceName = this.resourceName + '/' + opts.archive + '/' + opts.type;
    }
});

export default FolderCollection;

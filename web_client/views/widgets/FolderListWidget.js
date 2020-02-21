import $ from 'jquery';
import _ from 'underscore';

import View from 'girder/views/View';

import FolderCollection from '../../collections/FolderCollection';
import FolderListTemplate from '../../templates/widgets/folderList.pug';

/**
 * This widget shows a list of folders under a given parent.
 * Initialize this with a "parentType" and "parentId" value, which will
 * be passed to the folder GET endpoint.
 */
var FolderListWidget = View.extend({
    events: {
        'click a.archive-folder-list-link': function (event) {
            event.preventDefault();
            var cid = $(event.currentTarget).attr('archive-folder-cid');
            this.trigger('g:folderClicked', this.collection.get(cid));
        },
        // 'click a.g-show-more-folders': function () {
        //     this.collection.fetchNextPage();
        // },
        'change .g-list-checkbox': function (event) {
            const target = $(event.currentTarget);
            const cid = target.attr('archive-folder-cid');
            if (target.prop('checked')) {
                this.checked.push(cid);
            } else {
                const idx = this.checked.indexOf(cid);
                if (idx !== -1) {
                    this.checked.splice(idx, 1);
                }
            }
            this.trigger('g:checkboxesChanged');
        }
    },

    initialize: function (settings) {
        this.checked = [];
        this.type = settings.type;
        this.data = settings.data || {};
        this.collection = new FolderCollection();
        this.collection.rename({archive: 'SAIP', type: this.type});
        this.collection.on('g:changed', function () {
            window.test = this.collection;
            this.render();
            this.trigger('g:changed');
        }, this).fetch(this.data);
    },

    render: function () {
        this.checked = [];
        this.$el.html(FolderListTemplate({
            type: this.type,
            folders: this.collection.toArray(),
            hasMore: this.collection.hasNextPage()
        }));
        return this;
    },

    /**
     * Insert a folder into the collection and re-render it.
     */
    insertFolder: function (folder) {
        this.collection.add(folder);
        this.trigger('g:changed');
        this.render();
    },

    /**
     * Set all folder checkboxes to a certain checked state. The event
     * g:checkboxesChanged is triggered once after checking/unchecking everything.
     * @param {bool} checked The checked state.
     */
    checkAll: function (checked) {
        this.$('.g-list-checkbox').prop('checked', checked);

        this.checked = [];
        if (checked) {
            this.collection.each(function (model) {
                this.checked.push(model.cid);
            }, this);
        }

        this.trigger('g:checkboxesChanged');
    },

    recomputeChecked: function () {
        this.checked = _.map(this.$('.g-list-checkbox:checked'), function (checkbox) {
            return $(checkbox).attr('g-folder-cid');
        }, this);
    }
});

export default FolderListWidget;

import View from '@girder/core/views/View';

import SAIPTemplates from '../../templates/body/archivePage.pug';
import HierarchyWidget from '../widgets/HierarchyWidget';
import '../../stylesheets/widgets/hierarchyWidget.styl';

var ArchiveView = View.extend({
    initialize(settings) {
        this.$el.html(SAIPTemplates());
        this.render();
    },
    render() {
        if (!this.hierarchyWidget) {
            // The HierarchyWidget will self-render when instantiated
            this.hierarchyWidget = new HierarchyWidget({
                el: this.$('.g-archive-hierarchy-container'),
                type: 'projects',
                parentView: this
            });
        } else {
            this.hierarchyWidget
                .setElement(this.$('.g-archive-hierarchy-container'))
                .render();
        }
        return this;
    }
});

export default ArchiveView;

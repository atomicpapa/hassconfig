/* global customElements*/
/* global HTMLElement*/
customElements.whenDefined('card-tools').then(() => {
    var cardTools = customElements.get('card-tools');
    
    class KeepNotesCard extends cardTools.LitElement {
        setConfig(config) {
            if (!config.entity) {
                throw new Error('Please define entity');
            }
            
            this.config = config;
        }
        
        render() {
            return cardTools.LitHtml
            `
                ${this._renderStyle()}
                ${cardTools.LitHtml `
                    <ha-card>
                        <div class="header">
                            <div class="name">
                                ${this.cardTitle}
                            </div>
                        </div>
                        
                        <div>
                            ${this.unchecked.length > 0 ? cardTools.LitHtml `
                                ${this.unchecked.map(note =>
                                    cardTools.LitHtml `
                                        <div class="body flex">
                                            <div class="horizontal-flex">
                                                <div class="icon">
                                                    ${note['checked'] == true ? cardTools.LitHtml ` <ha-icon icon="mdi:checkbox-marked-outline"></ha-icon> ` : cardTools.LitHtml ` <ha-icon icon="mdi:checkbox-blank-outline"></ha-icon> `}
                                                </div>
                                                <div class="note">
                                                    ${note['text']}
                                                </div>
                                            </div>
                                        </div>
                                    `
                                )} ` : ''
                            }
                            ${(this.unchecked.length > 0) && (this.checked.length > 0) ? cardTools.LitHtml ` <hr> ` : ''} 
                            ${this.checked.length > 0 ? cardTools.LitHtml `
                                ${this.checked.map(note =>
                                    cardTools.LitHtml `
                                        <div class="body flex">
                                            <div class="horizontal-flex">
                                                <div class="icon">
                                                    ${note['checked'] == true ? cardTools.LitHtml ` <ha-icon icon="mdi:checkbox-marked-outline"></ha-icon> ` : cardTools.LitHtml ` <ha-icon icon="mdi:checkbox-blank-outline"></ha-icon> `}
                                                </div>
                                                <div class="note checked">
                                                    ${note['text']}
                                                </div>
                                            </div>
                                        </div>
                                    `
                                )} ` : ''
                            }
                            ${(this.unchecked.length == 0) && (this.checked.length == 0) ? cardTools.LitHtml `
                                <div class="body flex">
                                    <div>
                                        You don't have any notes!
                                    </div>
                                </div>
                            ` : ''}
                        </div>
                    </ha-card>
                `}
            `;
        }
        
        _renderStyle() {
            return cardTools.LitHtml `
                <style>
                    ha-card {
                        padding: 16px;
                    }
                    .header {
                        padding: 0;
                        @apply --paper-font-headline;
                        line-height: 40px;
                        color: var(--primary-text-color);
                        padding: 4px 0 12px;
                    }
                    .body {
                        padding-top: 0.5em;
                        padding-bottom: 0.5em;
                        margin-left: 1em;
                    }
                    .flex {
                        display: flex;
                        justify-content: space-between;
                    }
                    .icon {
                        margin-right: 1em;
                        display: inline-block;
                    }
                    .note {
                        display: inline;
                        vertical-align: middle;
                    }
                    .checked {
                        text-decoration: line-through;
                    }
                    .horizontal-flex {
                        display: flex
                    }
                </style>
            `;
        }
        
        set hass(hass) {
            this._hass = hass;
            
            const entity = hass.states[this.config.entity];
            this.cardTitle = this.config.title == null ? entity.attributes['notes']['name'] : this.config.title;
            
            this.notes = entity.attributes['notes']['data'];
            
            var checked = [];
            var unchecked = [];
            
            this.notes.forEach(function(item) {
                if (item['checked'] == true) {
                    checked.push(item);
                } else {
                    unchecked.push(item);
                }
            });
            
            this.checked = checked;
            this.unchecked = unchecked;
            
            this.requestUpdate();
        }
    }
    
    customElements.define("keep-notes-card", KeepNotesCard);
});

setTimeout(() => {
    if(customElements.get('card-tools')) return;
    customElements.define('keep-notes-card', class extends HTMLElement{
        setConfig() { throw new Error("Can't find card-tools. See https://github.com/thomasloven/lovelace-card-tools");}
        
    });
}, 2000);

//${this.notShowing.length > 0 ? cardTools.LitHtml`<div class="secondary">Look in Grocy for ${this.notShowing.length} more chores...</div>` : ""}

// css selector for the hidden input containing the contributors form data
const hiddenSelector = '#dataset-edit input[name="contributors"]';
// helper function for retrieving an object of {contributor_id: contributor} from the hidden input
let allContributors  = () => {
    return JSON.parse($(hiddenSelector).first().val() || '[]')
};

function updateHiddenInput(newList) {
    $(hiddenSelector).val(JSON.stringify(newList));
}

function moveUp(el) {
    let allContrib    = allContributors();
    let sortedContrib = Object.values(allContributors()).sort((a, b) => a.order - b.order)
                              .map((c) => c.id);
    let itemId        = el.parentElement.dataset.id
    let currentIx     = sortedContrib.indexOf(itemId);
    if (currentIx <= 0) {
        console.log(itemId);
        console.log(sortedContrib);
        return;
    }

    // update the elements
    let rows    = $('#contributor-rows .contributor-edit-row');
    let itemRow = $(rows[currentIx]);
    let prevRow = $(rows[currentIx - 1]);
    itemRow.find('[data-field=order]').val(currentIx - 1)
    prevRow.find('[data-field=order]').val(currentIx)
    prevRow.before(itemRow);

    // update the hidden input
    let prevItemId         = sortedContrib[currentIx - 1];
    let item               = allContrib[itemId];
    let prevItem           = allContrib[prevItemId];
    item.order             = currentIx - 1;
    prevItem.order         = currentIx;
    allContrib[itemId]     = item;
    allContrib[prevItemId] = prevItem;
    $(hiddenSelector).val(JSON.stringify(allContrib));
}

function moveDown(el) {
    let allContrib    = allContributors();
    let sortedContrib = Object.values(allContributors()).sort((a, b) => a.order - b.order)
                              .map((c) => c.id);
    let itemId        = el.parentElement.dataset.id
    let currentIx     = sortedContrib.indexOf(itemId);
    if (currentIx >= sortedContrib.length - 1) {
        return;
    }

    // update the elements
    let rows    = $('#contributor-rows .contributor-edit-row');
    let itemRow = $(rows[currentIx]);
    let nextRow = $(rows[currentIx + 1]);
    itemRow.find('[data-field=order]').val(currentIx + 1)
    nextRow.find('[data-field=order]').val(currentIx)
    nextRow.after(itemRow);

    // update the hidden input
    let nextItemId         = sortedContrib[currentIx + 1];
    let item               = allContrib[itemId];
    let nextItem           = allContrib[nextItemId];
    item.order             = currentIx + 1;
    nextItem.order         = currentIx;
    allContrib[itemId]     = item;
    allContrib[nextItemId] = nextItem;
    $(hiddenSelector).val(JSON.stringify(allContrib));
}

function deleteRow(el) {
    let allContrib     = allContributors();
    let itemId         = el.parentElement.dataset.id;
    let item           = allContrib[itemId];
    item.update        = false;
    item.delete        = true;
    allContrib[itemId] = item;
    $(hiddenSelector).val(JSON.stringify(allContrib));

    $(`.contributor-edit-row[data-id=${itemId}]`).addClass('to-delete')
}

function editRow(el) {
    let parent = $(el.parentElement);
    parent.siblings('.contributor-edit-fields').removeClass('contributor-field-hidden')
    parent.siblings('.contributor-display-fields').addClass('contributor-field-hidden');
}

function updateFromOrcid(el) {
    let allContrib = allContributors();
    let itemId     = el.parentElement.dataset.id;
    let item       = allContrib[itemId];
    let jEl = $(el);
    jEl.addClass('fa-spin');
    fetch('/api/3/action/contributor_orcid_update', {
        method:      'POST',
        mode:        'cors',
        cache:       'no-cache',
        credentials: 'same-origin',
        headers:     {
            'Content-Type': 'application/json'
        },
        redirect:    'follow',
        referrer:    'no-referrer',
        body:        JSON.stringify({
                                        'id': itemId
                                    }),
    }).then(response => {
        return response.json();
    }).then(data => {
        if (!data.success) {
            console.error(data.error);
            return;
        }
        data.result.order  = item.order;
        allContrib[itemId] = data.result;
        updateHiddenInput(allContrib);
        updateRow(jEl.parents('.contributor-edit-row'), data.result, []);
    }).finally(() => {
        jEl.removeClass('fa-spin');
    })
}

function updateRow(rowElement, rowContent, skip) {
    // remove 'skip-input' class from everything in the row
    rowElement.find('.skip-input').removeClass('skip-input');
    // set the values in the edit boxes
    rowElement.find('.contributor-field')
              .each((x, y) => {
                  // get the input element from the cell
                  let input = $(y).find('input')[0];
                  // skip/hide fields listed in 'skip'
                  if (skip.includes(input.dataset.field)) {
                      $(y).addClass('skip-input');
                  }
                  // if it's a list, join it with semicolons
                  else if (input.dataset.fieldType === 'list') {
                      input.value = (rowContent[input.dataset.field] || []).join('; ');
                  }
                  // otherwise set the value of the input to the dict value
                  else {
                      input.value = rowContent[input.dataset.field] || '';
                  }
              })
    // set the display values
    let nameContent = `${rowContent.surname}, ${rowContent.given_names}`;
    if (rowContent.orcid !== null && rowContent.orcid !== undefined) {
        nameContent += ` (<a href="https://orcid.org/${rowContent.orcid}"><i class="fab fa-orcid"></i> ${rowContent.orcid}</a>)`;
    }
    else {
        rowElement.find('.refresh-contrib').remove()
    }
    rowElement.find('.contributor-names').html(nameContent);
    rowElement.find('.contributor-affiliations')
              .html((rowContent.affiliations || []).join('; '))
}

$(document).ready(function () {
    // CONSTANTS/SELECTORS =========================================================================
    // contains the displayed rows
    let container      = $('#contributor-rows');
    // a *string* of template HTML
    let templateHtml   = $('#contributor-new-edit-row')[0].outerHTML;
    let searchBox      = $('#contributor-search-input');
    let orcidSearchBox = $('#contributor-search-orcid-input');
    let orcidCheck     = $('#contributor-search-orcid');
    let selectBox      = $('#contributor-search-options');
    let portalGroup    = $('#contributor-search-options #portal-group');
    let orcidGroup     = $('#contributor-search-options #orcid-group');
    let loader         = $('#contributor-search-loading')

    // FUNCTIONS ===================================================================================
    // generic function to add a new row/contributor to the UI, either from the existing list at
    // initialisation or as a new row during usage
    function addRow(rowIndex, rowId, rowContent, skip, disableEdit) {
        // replace 'new' in the template string with the rowIndex
        let newRow = templateHtml.replace(/new/g, rowIndex);
        // add the modified template string to the container
        container.append(newRow);
        // get a jquery reference to the new element/row
        let newRowElem = container.find(`#contributor-${rowIndex}-edit-row`);
        // set the correct id
        newRowElem.find('[data-id]').each((x, y) => {
            y.dataset.id = rowId;
        })
        newRowElem[0].dataset.id = rowId;

        updateRow(newRowElem, rowContent, skip);

        if (disableEdit) {
            newRowElem.find('.contributor-edit-fields').addClass('contributor-field-hidden');
        }
        else {
            newRowElem.find('.contributor-display-fields').addClass('contributor-field-hidden');
        }

        // update the relevant hidden input whenever one of these fields is changed
        newRowElem.find('.contributor-field input').on('change', (e) => {
            // get the current content of the hidden input
            let currentContribList = allContributors();
            // get the changed value of the input
            let newValue           = e.target.value;
            // if it's a list, extract individual items by splitting at semicolons (yeah I know)
            if (e.target.dataset.fieldType === 'list') {
                newValue = newValue.split('; ').map(v => v.trim());
            }
            // update just that value in the dict from the hidden input
            currentContribList[e.target.dataset.id][e.target.dataset.field] = newValue;
            // if it's an existing contributor, mark it as updated
            if (!Object.keys(currentContribList)
                       .includes(e.target.dataset.id) || !currentContribList[e.target.dataset.id].new) {
                currentContribList[e.target.dataset.id].update = true
            }
            // set the value of the hidden input to the updated dict
            updateHiddenInput(currentContribList);
        })

        return newRowElem;
    }

    function autocomplete() {
        portalGroup.children().remove();
        orcidGroup.children().remove();
        portalGroup.addClass('hideme');
        orcidGroup.addClass('hideme');
        loader.addClass('fa-spin');
        loader.removeClass('hideme')

        let includeOrcid = orcidCheck.prop('checked');

        fetch('/api/3/action/contributor_autocomplete', {
            method:      'POST',
            mode:        'cors',
            cache:       'no-cache',
            credentials: 'same-origin',
            headers:     {
                'Content-Type': 'application/json'
            },
            redirect:    'follow',
            referrer:    'no-referrer',
            body:        JSON.stringify({
                                            'surname':       searchBox.val(),
                                            'orcid':         orcidSearchBox.val(),
                                            'include_orcid': includeOrcid
                                        }),
        }).then(response => {
            return response.json();
        }).then(data => {
            if (!data.success) {
                console.error(data);
                return;
            }

            console.log(data.result)

            // add results from our database
            data.result.portal.forEach(r => {
                let optionContent = `${r.surname}, ${r.given_names}`;
                if (r.orcid !== null && r.orcid !== undefined) {
                    optionContent += ` (${r.orcid})`;
                }
                portalGroup.append(new Option(optionContent, JSON.stringify(r)));
            });
            // add results from the ORCID API
            data.result.orcid.forEach(r => {
                orcidGroup.append(new Option(`${r.surname}, ${r.given_names} (${r.orcid})`, JSON.stringify(r)));
            });
            // add an info line showing that there are more results
            if (data.result.orcid_remaining > 0) {
                orcidGroup.append(`<option disabled>+ ${data.result.orcid_remaining} more results from ORCID</option>`)
            }

            // default selections
            if (data.result.portal.length > 0) {
                selectBox.val(JSON.stringify(data.result.portal[0]));
            }
            else if (data.result.orcid.length > 0) {
                selectBox.val(JSON.stringify(data.result.orcid[0]));
            }
            else {
                selectBox.val('blank')
            }

            // only show groups if they have content
            if (data.result.portal.length > 0) {
                portalGroup.removeClass('hideme');
            }
            if (data.result.orcid.length > 0) {
                orcidGroup.removeClass('hideme');
            }
        }).finally(() => {
            loader.removeClass('fa-spin');
            loader.addClass('hideme')
        });
    }

    // SETUP =======================================================================================
    // display the contributor list
    Object.entries(allContributors()).sort((a, b) => {
        return a[1].order - b[1].order;
    }).forEach((e, ix) => {
        e[1].new = false;
        addRow(ix, e[0], e[1], [], true)
    })

    // LISTENERS ===================================================================================

    $('#contributor-search-button').click(autocomplete);

    $('#contributor-add-button').on('click', (e) => {
        let selectBox   = $('#contributor-search-options');
        let allContrib  = allContributors()
        let rowIx       = Object.entries(allContrib).length
        let rowId       = `new-${rowIx}`
        let selection   = selectBox.val()
        let manualEntry = selection === 'blank';
        let newContrib;

        if (manualEntry) {
            newContrib = {
                id:    rowId,
                order: rowIx,
                new:   true
            };
        }
        else {
            newContrib       = JSON.parse(selection);
            newContrib.order = rowIx;
            if (newContrib.id === undefined) {
                newContrib.new = true;
                newContrib.id  = rowId;
            }
        }

        // add the new contributor dict to the hidden input
        allContrib[newContrib.id] = newContrib
        $(hiddenSelector).val(JSON.stringify(allContrib));

        // add a new row
        let newRow = addRow(rowIx, newContrib.id, newContrib, manualEntry ? ['orcid'] : [], !manualEntry)
        newRow.addClass('is-new');
    })
});
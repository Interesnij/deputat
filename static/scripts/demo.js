
$('.sel').each(function() {
  $(this).children('select').css('display', 'none');

  var $current = $(this);

  $(this).find('option').each(function(i) {
    if (i == 0) {
      $current.prepend($('<div>', {
        class: $current.attr('class').replace(/sel/g, 'sel__box')
      }));

      var placeholder = $(this).text();
      $current.prepend($('<span>', {
        class: $current.attr('class').replace(/sel/g, 'sel__placeholder'),
        text: placeholder,
        'data-placeholder': placeholder
      }));

      return;
    }

    $current.children('div').append($('<span>', {
      class: $current.attr('class').replace(/sel/g, 'sel__box__options'),
      text: $(this).text(),
      slug: $(this).val()
    }));
  });
});

// Toggling the `.active` state on the `.sel`.
$('.sel').click(function() {
  $(this).toggleClass('active');
});

// Toggling the `.selected` state on the options.
$('.sel__box__options').click(function() {
  var txt = $(this).text();
  var index = $(this).index();
  var slug = $(this).attr("slug");

  console.log(slug)

  $(this).siblings('.sel__box__options').removeClass('selected');
  $(this).addClass('selected');

  var $currentSel = $(this).closest('.sel');
  $currentSel.children('.sel__placeholder').text(txt);
  $currentSel.children('select').prop('selectedIndex', index + 1);

  block = this.parentElement.parentElement.nextElementSibling;
  map = this.parentElement.parentElement.parentElement.previousElementSibling;

  if (slug == '') {
    block.innerHTML = "";
    svg_list = map.querySelectorAll("path");
    for (var i = 0; i < svg_list.length; i++) {
      svg_list[i].style.fill = "rgba(0,0,0,0.15)";
    }
  } else {
    var link = window.XMLHttpRequest ? new XMLHttpRequest() : new ActiveXObject( 'Microsoft.XMLHTTP' );
    link.open( 'GET', "/list/region/" + slug + "/", true );
    link.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    link.onreadystatechange = function () {
      if ( link.readyState == 4 ) {
          if ( link.status == 200 ) {
              block.innerHTML = link.responseText;
              svg_list = map.querySelectorAll("path");
              for (var i = 0; i < svg_list.length; i++) {
                svg_list[i].style.fill = "rgba(0,0,0,0.15)";
              }
              svg = map.querySelector('[data-slug=' + '"' + slug + '"' + ']');
              svg.style.fill = "green";
          }
      }
  };
  link.send( null );
  };
});

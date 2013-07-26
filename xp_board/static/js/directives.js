var directiveTemplateRoot = '/static/js/directive_templates/';
angular.module('XPBoard').directive(
  'stickyColumnView', function() {
    return {
      restrict: 'E',
      replace: true,
      scope: {
        ticketsByTitle: '=ticketsByTitle',
        searchText: '=searchText'
      },
      templateUrl: directiveTemplateRoot + 'sticky_column_view.html',
      link: function(scope) {}
    }
  }
).directive(
  'stickyColumn', function() {
    return {
      restrict: 'E',
      replace: true,
      scope: {
        tickets: '=tickets',
        title: '=title',
        searchText: '=searchText'
      },
      templateUrl: directiveTemplateRoot + 'sticky_column.html',
      link: function(scope, element, attrs) {
        scope.byOwnerOrReviewer = function(ticket) {
          if(!scope.searchText) return false;
          var matchers = scope.searchText.split("|");
          return _.any(matchers, function(matcher) {
            return ticket.owner.indexOf(matcher) > -1 || (
              ticket.review_requests.length > 0 &&
                ticket.review_requests[0].primary_reviewer.indexOf(matcher) > -1
            );
          });
        }
      }
    }
  }
).directive(
  'sticky', ['URLGenerator', 'config', function(URLGenerator, config) {
    return {
      restrict: 'E',
      replace: true,
      scope: {
        ticket: '=ticket'
      },
      templateUrl: directiveTemplateRoot + 'sticky.html',
      link: function(scope, element, attrs) {
        scope.URLGenerator = URLGenerator;
        scope.style = {"background-color": config.user_colors[scope.ticket.owner]};
      }
    }
  }]
).directive(
  'userTable', function() {
      return {
        restrict: 'E',
        replace: true,
        scope: {
          username: '=username',
          ownedTickets: '=ownedTickets'
        },
        templateUrl: directiveTemplateRoot + 'user_table.html',
        link: function(scope) {
          scope.ticketsByStatus = _.groupBy(scope.ownedTickets, 'status');
        }
      }
    }
).directive(
  'ticketTable', function() {
    return {
      restrict: 'E',
      replace: true,
      scope: {
        tickets: '=tickets',
        title: '=title'
      },
      templateUrl: directiveTemplateRoot + 'ticket_table.html',
      link: function(scope) {}
    }
  }
);
                                    

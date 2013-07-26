angular.module('XPBoard').factory('TicketData', ['$http', function($http) {
  function TicketData(usernames) {
    this.usernames = usernames || [];
    this.ticketCache = null;
  }

  TicketData.prototype.ticketsByUsernames = function(usernames) {
    var result;
    $.ajax({
      url: '/tickets',
      data: {
        user: usernames || this.usernames
      },
      async: false,
      traditional: true,
      success: function(users) {
        result = JSON.parse(users);
      }
    });
    return result;
  }

  TicketData.prototype.__defineGetter__('tickets', function() {
    if(this.ticketCache != null) return this.ticketCache;
    this.ticketCache = this.ticketsByUsernames();
    return this.ticketCache;
  });
  return new TicketData();
}]).factory('URLGenerator', [function() {
  return {
    getReviewRequestURL: function(reviewRequestID) {
      
    },
    getTicketURL: function(ticketID) {
      
    }
  }
}]);

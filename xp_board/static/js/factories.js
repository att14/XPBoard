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
}]).factory('URLGenerator', ['config', function(config) {
  return {
    getReviewRequestURL: function(reviewRequestID) {
      return "https://" + config.rb_url + '/r/' + reviewRequestID
    },
    getTicketURL: function(ticketID) {
      return "https://" + config.trac_url + '/ticket/' + ticketID
    }
  }
}]).factory('config', ['$http', function($http) {
  var config = {
  }
  $http.get('/config').success(function(data) {
    _.extend(config, data);
  });
  return config;
}]).factory('status', function() {
  return {
    remapping: {
      "new": "New",
      "assigned": "Assigned",
      "in_review": "In Review",
      "ship_it": "Ship-It",
      "closed": "In Production"
    },
    order: ["new", "assigned", "in_review", "ship_it", "closed"]
  };
});
